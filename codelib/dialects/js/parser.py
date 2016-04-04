import sys
from antlr4 import *
from ECMAScriptLexer import ECMAScriptLexer
from ECMAScriptParser import ECMAScriptParser
from ECMAScriptListener import ECMAScriptListener

class Parser(object):

    class FuncPrinter(ECMAScriptListener):
        def on_function(self, ctx):
            print('###### Function ######')
            print('Identifier:', ctx.Identifier())
            parameter_list = ctx.formalParameterList()
            if parameter_list is not None:
                print('Arguments:', parameter_list.getText())
            else:
                print('Arguments: None')
            body = ctx.functionBody()
            print('# statements in body',
                    body.sourceElements().getChildCount())
            print('Body text:', repr(body.getText()))
            print('\n')

        def exitFunctionExpression(self, ctx):
            self.on_function(ctx)

        def exitFunctionDeclaration(self, ctx):
            self.on_function(ctx)

        def on_for(self, ctx):
            print('###### For loop ######')
            sequence = ctx.expressionSequence()
            conditional = sequence[0].singleExpression(0)
            increment = sequence[1].singleExpression(0)
            print('Conditional:', conditional.getText())
            print('Increment:', increment.getText())
            print('Body:', ctx.statement().getText())
            print('\n')

        def exitForStatement(self, ctx):
            self.on_for(ctx)

        def exitForVarStatement(self, ctx):
            self.on_for(ctx)

        def exitForInStatement(self, ctx):
            self.on_for(ctx)

        def exitForVarInStatement(self, ctx):
            self.on_for(ctx)

    def parse(self, filename):
        print('Parsing', filename)
        lexer = ECMAScriptLexer(FileStream(filename))
        parser = ECMAScriptParser(CommonTokenStream(lexer))
        printer = self.FuncPrinter()
        walker = ParseTreeWalker()
        walker.walk(printer, parser.program())

if __name__ == '__main__':
    parser = Parser()
    parser.parse(sys.argv[1])
