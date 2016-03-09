"""
Classes to uniformly represent (blockly) code, independant of its original
representation. Different connectors can be written to parse app-specific
exports of code and instantiate these classes.
"""
class Node(object):
    def __init__(self, block=[]):
        self.block = block

    def append_node(self, node):
        self.block.append(node)

    def contains(self, node_type):
        return any(n._contains(node_type) for n in self.block)

    def _contains(self, node_type):
        if isinstance(self, node_type):
            return True
        return any(n._contains(node_type) for n in self.block)

    def find(self, node_type):
        nodes = []
        for n in self.block:
            nodes += n._find(node_type)
        return nodes

    def _find(self, node_type):
        nodes = [self] if isinstance(self, node_type) else []
        for n in self.block:
            nodes += n._find(node_type)
        return nodes

    def node_count(self):
        return sum(n._node_count() for n in self.block)

    def _node_count(self):
        return 1 + sum(n._node_count() for n in self.block)

    def __str__(self):
        return "<{} {}>".format(type(self), self.block)

class Root(Node):
    def __init__(self, block):
        super().__init__(block)

    def __str__(self):
        return "START [{}]".format(", ".join(str(n) for n in self.block))

class Statement(Node):
    def __init__(self, name):
        super().__init__()
        self.name = name

    def __str__(self):
        return "{}".format(self.name)

class IfElse(Node):
    def __init__(self, condition, if_block, else_block=None):
        super().__init__(if_block)
        self.condition = condition
        self.else_block = else_block

    def __str__(self):
        return "IF {} THEN [{}] ELSE [{}]".format(self.condition,
            ", ".join(str(n) for n in self.block), 
            ", ".join(str(n) for n in self.else_block)
                if self.else_block is not None else None)

class For(Node):
    def __init__(self, repetition, block):
        super().__init__(block)
        self.repetition = repetition

    def __str__(self):
        return "FOR {} TIMES [{}]".format(self.repetition, 
            ", ".join(str(n) for n in self.block))

class While(Node):
    def __init__(self, condition, block):
        super().__init__(block)
        self.condition = condition

    def __str__(self):
        return "WHILE {} DO [{}]".format(self.condition,
            ", ".join(str(n) for n in self.block))

