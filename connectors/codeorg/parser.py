"""Module containing parsers for code.org submissions."""
from bs4 import BeautifulSoup
from codelib import Root, Statement, While, For, IfElse

def codeorg_parse(xml):
    """Parse incoming code submission from xml"""
    soup = BeautifulSoup(xml, 'xml')
    return codeorg(soup.xml.contents[0])

def codeorg(node):
    """Parse BS4 node containing code submission."""
    if 'when_run' in node['type']:
        return Root(codeorg(node.next.contents[0]))
    elif '_if' in node['type']:
        parsed = IfElse(
            node.title.string,
            codeorg(node.statement.contents[0]),
            codeorg(node.statement.next_sibling.contents[0]) if \
                node.statement.next_sibling is not None else None)
    elif any([x in node['type'] for x in ('_forever', '_while', '_until')]):
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
    for child_node in node.contents:
        if child_node.name == 'next':
            siblings = codeorg(child_node.contents[0])
            break
    return [parsed] + siblings

