from bs4 import BeautifulSoup
from bs4.element import Tag, NavigableString
from codelib import *

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
    elif any(map(lambda x: x in node['type'], ('_forever', '_while', '_until'))):
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

