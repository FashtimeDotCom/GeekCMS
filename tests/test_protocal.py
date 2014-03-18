"""
Test Plan.

PluginIndex:
    test_unique:
        make sure plugin index is hashable and its uniqueness.

BaseResource, BaseProduct, BaseMessage, _BaseAsset:
    test_init:
        these class can not be initialized.

Manager:
    test_trace_one_class:
        initialize single derived class of [BaseResource, BaseProduct,
        BaseMessage,], make sure the manager can trace that instance.
    test_trace_multi_classes:
        initialize multiple derived classes of the same base class, make sure
        the manager of base class can trace multiple instances.
    test_usage:
        make sure bussinesses of manager, such as create, add, remove and so
        on, is correct.

ManagerProxyWithOwner:
    test_proxy:
        make sure the method with 'owenr' in signature is binded properly.

BasePlugin, SetUpPlugin, PluginController:
    test_init:
        ensure that BasePlugin would not be registered.
    test_register:
        ensure plugin is register by metaclass, and so as the process of
        retrieving plugins.
    test_theme_name:
        1. definde class-level theme attr.
        2. undefine class-level theme attr, but SetUpPlugin defines context
        theme.
        3. both class-level theme attr and context theme are defined. In
    test_plugin_name:
        1. define class-level plugin attr.
        2. undefine ...
    test_default_params:
        1. test run method with 0~3 defined parameters(exclude self).
        2. test run method with parameters more than 3.
    test_accept_parameters:
        make sure accept_parameters works.
    test_accept_owners:
        make sure accept_owners works, and that do not confilct with
        theme_name.

"""

import unittest
from collections import defaultdict
from geekcms import protocal


class ManagerTest(unittest.TestCase):

    def setUp(self):
        class TestClass:
            def __init__(self, owner):
                self.owner = owner

            def __repr__(self):
                return '{}({})'.format('TestCase', self.owner)

        self.TestClass = TestClass
        self.owner = 'testowner'
        self.manager = protocal.Manager(TestClass)

    def test_create(self):
        item = self.manager.create(self.owner)
        self.assertEqual(item.owner, self.owner)
        self.assertIsInstance(item, self.TestClass)

    def test_add_remove(self):
        item = self.TestClass(self.owner)
        self.assertEqual(self.manager, defaultdict(list))

        self.manager.add(item)
        self.assertDictEqual(
            dict(self.manager),
            {self.owner: [item]},
        )

        self.manager.remove(item)
        self.assertEqual(self.manager, defaultdict(list))

    def test_filter_keys_values(self):
        owner_1 = 'owner_1'
        owner_2 = 'owner_2'
        item_1 = self.manager.create(owner_1)
        item_2 = self.manager.create(owner_2)

        self.assertListEqual(self.manager.filter(owner_1), [item_1])
        self.assertListEqual(self.manager.filter(owner_2), [item_2])
        self.assertSetEqual(
            set(self.manager.keys()),
            {owner_1, owner_2},
        )
        self.assertSetEqual(
            set(self.manager.values()),
            {item_1, item_2},
        )

    def test_proxy(self):
        proxy = protocal.ManagerProxyWithOwner(self.owner, self.manager)

        item = proxy.create()
        self.assertDictEqual(
            dict(self.manager),
            {self.owner: [item]},
        )

        proxy.remove(item)
        self.assertEqual(self.manager, defaultdict(list))

        item = proxy.create()
        self.assertListEqual(proxy.filter(), [item])
        self.assertListEqual(proxy.keys(), [self.owner])
        self.assertListEqual(proxy.values(), [item])


class PluginIndexTest(unittest.TestCase):

    def test_plugin(self):
        item_1 = protocal.PluginIndex('a', 'b')
        item_2 = protocal.PluginIndex('a', 'c')
        self.assertEqual(item_1, 'a.b')
        self.assertNotEqual(item_1, item_2)


class _BaseAssetTest(unittest.TestCase):

    def setUp(self):
        class TestClass(protocal._BaseAsset):
            def __init__(self, owner):
                self.owner = owner

        self.TestClass = TestClass

    def test_init(self):
        owner = 'testowner'
        attr = 'testattr'

        item = self.TestClass(owner)
        self.assertEqual(item.owner, owner)

        item.attr = attr
        self.assertEqual(item.attr, attr)

        self.assertIsInstance(item, self.TestClass)

    def test_manager(self):
        owner = 'testowner'
        manager = self.TestClass.get_manager_with_fixed_owner(owner)
        item = manager.create()
        self.assertEqual(item.owner, owner)
        self.assertIsInstance(item, self.TestClass)

    def test_manager_attr_op(self):
        with self.assertRaises(Exception) as e:
            item = self.TestClass('testowner')
            # access
            item.objects
        with self.assertRaises(Exception) as e:
            item = self.TestClass('testowner')
            # assign
            item.objects = None
        with self.assertRaises(Exception) as e:
            # remove
            item = self.TestClass('testowner')
            del item.objects

    def test_resource_product_message(self):
        owner = 'testowner'

        class ResourceTest(protocal.BaseResource):
            def __init__(self, owner):
                self.owner = owner

        class ProductTest(protocal.BaseProduct):
            def __init__(self, owner):
                self.owner = owner

        self.assertEqual(
            issubclass(ResourceTest, protocal.BaseResource),
            True,
        )
        self.assertEqual(
            issubclass(ProductTest, protocal.BaseResource),
            False,
        )
        self.assertIsInstance(
            ResourceTest.objects.create(owner),
            ResourceTest,
        )


class PluginTest(unittest.TestCase):

    def setUp(self):
        protocal.SetUpPlugin.clean_up_registered_plugins()

    def test_plugin_registration(self):
        theme_name = 'testtheme'
        plugin_name = 'testplugin'

        class TestPlugin(protocal.BasePlugin):
            theme = theme_name
            plugin = plugin_name

            def __init__(self):
                pass

            def run(self, assets, messages):
                return assets, messages

        class MissPluginName(protocal.BasePlugin):
            theme = theme_name

            def __init__(self):
                pass

            def run(self, assets, messages):
                return assets, messages

        supposed_plugins = {
            protocal.PluginIndex(theme_name, plugin_name): TestPlugin,
            protocal.PluginIndex(theme_name, 'MissPluginName'): MissPluginName,
        }

        self.assertDictEqual(
            protocal.get_registered_plugins(),
            supposed_plugins,
        )

    def test_assets_filter(self):
        theme_name = 'a'
        noise_name = 'b'

        pcl = protocal.PluginController

        class TestPlugin(protocal.BasePlugin):
            theme = theme_name

            def __init__(self):
                pass

            @pcl.accept_parameters(pcl.RESOURCES, pcl.MESSAGES)
            def run(self, resources, messages):
                return resources, messages

        class TestResource(protocal.BaseResource):
            def __init__(self, owner):
                self.owner = owner

        class TestMessage(protocal.BaseMessage):
            def __init__(self, owner):
                self.owner = owner

        resource_manager =\
            TestPlugin.get_manager_bind_with_plugin(TestResource)
        message_manager =\
            TestPlugin.get_manager_bind_with_plugin(TestMessage)

        supposed_resources = set()
        supposed_messages = set()
        for i in range(10):
            supposed_resources.add(resource_manager.create())
            supposed_messages.add(message_manager.create())
            TestResource.objects.create(noise_name)
            TestMessage.objects.create(noise_name)

        plugin = TestPlugin()
        resources, messages = plugin.run(
            TestResource.objects.values(),
            None,
            TestMessage.objects.values(),
        )
        self.assertSetEqual(set(resources), supposed_resources)
        self.assertSetEqual(set(messages), supposed_messages)


if __name__ == '__main__':
    unittest.main()
