from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString

def codeorg_parse(xml):
    soup = BeautifulSoup(xml, 'xml')
    return codeorg(soup.xml.contents[0])

def codeorg(node):
    if 'when_run' in node['type']:
        return Root(codeorg(node.next.contents[0]))
    elif '_if' in node['type']:
        parsed = IfElse(node.title.string,
            codeorg(node.statement.contents[0]),
            codeorg(node.statement.next_sibling.contents[0])
                if node.statement.next_sibling is not None else None)
    elif '_forever' in node['type']:
        parsed = While('True', codeorg(node.statement.contents[0]))
    elif '_repeat' in node['type']:
        parsed = For(node.title.string, codeorg(node.statement.contents[0]))
    elif node.has_attr('inline'):
        parsed = Statement(node.block['type'])
    elif node.title is not None:
        parsed = Statement(node.title.string)
    else:
        parsed = Statement(node['type'])
    
    #Next is a BS function, so can't be used as a tag
    siblings = []
    for n in node.contents:
        if n.name == 'next':
            siblings = codeorg(n.contents[0])
            break
    return [parsed] + siblings


class Node(object):
    def __init__(self, block=[]):
        self.block = block

    def append_node(self, node):
        self.block.append(node)

    def contains(self, node_type):
        return any(n._contains(node_type) for n in self.block)

    def _contains(self, node_type):
        if self.isinstance(node_type):
            return True
        return any(n._contains(node_type) for n in self.block)

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

