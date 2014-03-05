
"""
Syntax:
    runtime_component ::= component_name (':' | '=') [NEWLINE] plugin_relation*

    plugin_relation ::= binary_relation_expr | unary_relation_expr NEWLINE
    binary_relation_expr ::= plugin_name
                             (left_relation | right_relation) plugin_name
    unary_plugin_expr ::= (plugin_name [left_relation])
                          | ([right_relation] plugin_name)

    left_relation ::= '<<' [decimalinteger]
    right_relation ::= [decimalinteger] '>>'
    component_name ::= identifier
    plugin_name ::= identifier

Semantics:
    1. "pre_load: my_loader": register plugin "my_loader" to component
    "pre_load".
    2. "pre_load: my_loader << my_filter": register plugins "my_loader" and
    "my_filter" to component "pre_load", with "my_loader" being executed before
    "my_filter".
    3. "pre_load: my_filter >> my_loader": has the same meaning as
    "pre_load: my_loader << my_filter".
    4. "pre_load: loader_a <<0 loader_b NEWLINE loader_c <<1 loader_b" the
    execution order would be "loader_c" --> "loader_a" --> "loader_b".
    "<<" is equivalent to "<<0", and "<< decimalinteger" is equivalent to
    "decimalinteger >>".
    5. "pre_load: my_loader <<": means "my_loader" would be executed before the
    other plugins within a component, unless another relation such as
    "anther_loader <<1" is established.
    6. "pre_load: >> my_filter": reverse meaning of "pre_load: my_loader <<".

Algorithm:
    1. lexical analysis: extract plugin relation expression from each physical
    line, transform to the format of (x <<p y).
        1.1 Extract left operand, operator and right operand. For expressions
        that only consist of one operand and no operator, for example,
        'x NEWLINE', remove such expressions and keep it for later processing.
        1.2 Transform 'x [p]>> y' to 'y <<[p] x', then transform '<<' to '<<0'
        1.3 Transform operand to the form of (theme, plugin), based on
        'theme.plugin'. If 'theme.' part is omitted, then automatically
        generate theme with respect to file's directory(where relation
        expressions were loaded).
        1.4 If x is missed, HEAD is added as x; If y is missed, TAIL is added
        as y;
        1.5 Init with classes, including items removed in 1.1.
    2. Generate relation groups.
    A relation group: {(x <<p y)| for x, all avaliable (p, y) in expressions}.
        2.1 Sort expressions(x <<p y) with respect to x's value, then with p's
        value. Generate raw relation groups.
        2.2 For every relation groups, tranlate all its relations (x <<p1 y1,
        x <<p2 y2, ..., x <<pn yn) to (x < y1, y1 < y2, ..., yn-1 < yn). Notice
        that '<' means 'x is executed earlier then y', in order to distingush
        with '<<', since 'x << y1, x << y2' cause syntax error.
        2.3 Sort expressions generated by 2.2, regenerate relation groups.
    3. Generate order of plugin execution.
        Input: sorted relation groups.
        Output: sequence of plugin execution.

        order = a queue
        left_behind = a set initiated with items removed in 1.1.
        for i = next relation group:
            x = i's left operand(same in expression of a relation group)
            y_set = i's all right operands.

            if x in left_behind, remove x from left_behind.
            push x to order(append it).

            for y in y_set:
                if y in queue:
                    stop processing, there must be error.
                else:
                    add y to left_behind it y not in left_behind.

        if left_behind is not empty, then push all its items to order.
        return order
"""


class SequenceParser:

    def __init__(self, plain_text):
        pass
