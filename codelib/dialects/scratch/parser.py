import json

from codelib.dialects import Dialect

class Node(object):
    control_blocks = ['doIf', 'doIfElse', 'doUntil', 'doRepeat', 'doForever']

    def __init__(self, code):
        self.code = code
    
    def walk(self, parser):
        if self.code == None or len(self.code) == 0:
            return
        
        elif self.code[0] in self.control_blocks:
            parser.node(self.code)
            
            if self.code[0] == 'doIfElse':
                parser.enter('If', self.code)
                Node(self.code[2]).walk(parser)
                
                parser.enter('Else', self.code)
                Node(self.code[3]).walk(parser)
            else:
                parser.enter(self.code[0][2:], self.code)

                if self.code[0] == 'doForever':
                    Node(self.code[1]).walk(parser)
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
        self.done = False
        self.state = []
    
    def enter(self, node_type, node):
        pass

    def node(self, node):
        pass

    def exit(self):
        pass

    def result(self):
        self.done = True
        return self.state

class ParserList(Parser):
    def __init__(self, parsers):
        self.parsers = parsers
    
    def enter(self, *args):
        self._loop('enter', args)

    def node(self, *args):
        self._loop('node', args)

    def exit(self, *args):
        self._loop('exit', args)

    def result(self, *args):
        return self._loop('result', args)

    def _loop(self, func, args):
        return [getattr(parser, func)(*args) for parser in self.parsers]

class GetControlNode(Parser):
    def __init__(self, node_type):
        super().__init__()
        self.node_type = node_type

    def enter(self, node_type, node):
        if self.node_type == node_type:
            self.state.append(node)
   
class HasControlNode(GetControlNode):
    def result(self):
        return len(super().result()) > 0

class GetSequenceCounts(Parser):
    def __init__(self):
        super().__init__()
        self.count = 0
        self.depth = 0
    
    def enter(self, node_type, node):
        depth += 1
    
    def node(self, node):
        self.count += 1

    def exit(self):
        depth -= 1
        if depth == 0:
            self.state.append(self.count)
            self.count = 0

class HasSequenceLength(GetSequenceCounts):
    def __init__(self, min_length):
        super().__init__()
        self.min_length = min_length
    
    def result(self):
        return max(super().result()) >= self.min_length

class CodeRepetition(Parser):
    def __init__(self, min_count):
        super().__init__()
        self.min_count = min_count
        self.occurences = []

    def node(self, node):
        if self.occurences == [] or self.occurences[0] == node:
            self.occurences.append(node)
        else:
            self._check_occ() 
            self.occurences = [node]

    def exit(self):
        self._check_occ() 
        self.occurences = []
    
    def _check_occ(self):
        if len(self.occurences) >= self.min_count:
            self.state.append(self.occurences)

class ScratchDialect(Dialect):
    starting_blocks = ['whenGreenFlag', 'whenKeyPressed', 'whenClicked',
        'whenSceneStarts', 'whenSensorGreaterThan', 'whenIReceive', 
        'whenCloned', 'procDef']

    def __init__(self, code):
        self.code = json.loads(code)['children']

        self.parser_def = {
            'has_seq': HasSequenceLength(2),
            'has_if': HasControlNode('If'),
            'has_ifelse': HasControlNode('Else'),
            'has_for': HasControlNode('Repeat'),
            'has_while': HasControlNode('Until'),
            'has_loop': HasControlNode('Forever'),
            'get_if': GetControlNode('If'),
            'repeats': CodeRepetition(3)
        }

        self.parse('has_seq', 'has_if', 'has_ifelse', 'has_for', 'has_while')
    

    def parse(self, *parsers):
        parser_list = ParserList([self.parser_def[parser] for parser in 
            parsers if not parser.done])
        
        if len(parser_list) > 0:
            for sprite in self.code:
                for elem in sprite.get('scripts', []):
                    line = elem[2]
                    if line[0][0] in self.starting_blocks:
                        StartNode(line[0], line[1:]).walk(parser_list)
        
        return [self.parser_def[parser].result() for parser in parsers]

    def has_seq(self):
        return self.parse('has_seq')[0]

    def has_if(self):
        return self.parse('has_if')[0]

    def has_ifelse(self):
        return self.parse('has_ifelse')[0]
    
    def has_for(self):
        return self.parse('has_for')[0]
    
    def has_while(self):
        return self.parse('has_while')[0]

