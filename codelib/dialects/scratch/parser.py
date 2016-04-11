import json
import unicodedata
import requests

class Node(object):
    control_blocks = ['doIf', 'doIfElse', 'doUntil', 'doRepeat', 'doForever']

    def __init__(self, code):
        self.code = code
    
    def walk(self, parser):
        if self.code == None or len(self.code) == 0:
            return
        elif self.code[0] in self.control_blocks:
            parser.enter(self.code[0][2:], self.code)

            if self.code[0] == 'doForever':
                Node(self.code[1]).walk(parser)
            elif self.code[0] == 'doIfElse':
                Node(self.code[2]).walk(parser)
                Node(self.code[3]).walk(parser)
            else:
                Node(self.code[2]).walk(parser)
        elif type(self.code[0]) is list:
            for block in self.code:
                Node(block).walk(parser)

            parser.exit()
        else:
            parser.node(self.code)


class StartNode(Node): 
    def __init__(self, condition, code):
        super().__init__(code)
        self.condition = condition

    def walk(self, parser):
        parser.enter(self.condition[0], self.code)
        Node(self.code).walk(parser)

class Parser(object):
    def __init__(self):
        self.state = []
    
    def enter(self, node_type, node):
        pass

    def node(self, node):
        pass

    def exit(self):
        pass

    def result(self):
        return self.state

class GetControlNode(Parser):
    def __init__(self, node_type):
        super().__init__()
        self.node_type = node_type

    def enter(self, node_type, node):
        if self.node_type == node_type:
            self.state.append(node)
   
class HasControlNode(GetControlNode):
    def result(self):
        return len(self.state) > 0

class CodeRepetition(Parser):
    def __init__(self, min_count):
        super().__init__()
        self.min_count = min_count
        self.occurences = []

    def node(self, node):
        if self.occurences == [] or self.occurences[0] == node:
            self.occurences.append(node)
        else:
            if len(self.occurences) >= self.min_count:
                self.state.append(self.occurences[:])
            self.occurences = [node]

    def exit(self):
        if len(self.occurences) >= self.min_count:
            self.state.append(self.occurences[:])
        self.occurences = []

class Dialect(object):
    starting_blocks = ['whenGreenFlag', 'whenKeyPressed', 'whenClicked',
        'whenSceneStarts', 'whenSensorGreaterThan', 'whenIReceive', 
        'whenCloned', 'procDef']

    def __init__(self, code):
        self.code = json.loads(code)['children']
    
    def walk(self, parser):
        for sprite in self.code:
            for elem in sprite.get('scripts', []):
                line = elem[2]
                if line[0][0] in self.starting_blocks:
                    StartNode(line[0], line[1:]).walk(parser)

        return parser.result()
    
    def get_ifs(self):
        return self.walk(GetControlNode('If')) + \
            self.walk(GetControlNode('IfElse'))

    def has_while(self):
        return self.walk(HasControlNode('Until'))

    def repeats(self):
        return self.walk(CodeRepetition(3))
    

d = Dialect(requests.get('https://cdn.projects.scratch.mit.edu/internalapi/project/104917701/get/411829921a3ecc03c0c685738c184fe9').text)
print(d.get_ifs())
print(d.has_while())
print(d.repeats())

