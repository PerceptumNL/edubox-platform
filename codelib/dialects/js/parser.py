import sys
from antlr4 import *
from .ECMAScriptLexer import ECMAScriptLexer
from .ECMAScriptParser import ECMAScriptParser
from .ECMAScriptListener import ECMAScriptListener

from codelib.dialects import Dialect

class ScriptListener(ECMAScriptListener):

    dialect = None

    def __init__(self, dialect):
        self.dialect = dialect

    def enterStatement(self, ctx):
        self.dialect.lines += 1

    def exitFunctionExpression(self, ctx):
        identifier = ctx.Identifier()
        if identifier is not None:
            identifier = identifier.getText()

        arguments = ctx.formalParameterList()
        if arguments is not None:
            arguments = arguments.getText()

        self.dialect.on_function(identifier, arguments)

    def exitFunctionDeclaration(self, ctx):
        self.exitFunctionExpression(ctx)

    def exitForStatement(self, ctx):
        sequence = ctx.expressionSequence()
        conditional = sequence[0].singleExpression(0)
        if conditional is not None:
            conditional = conditional.getText()

        increment = sequence[1].singleExpression(0)
        if increment is not None:
            increment = increment.getText()

        self.dialect.on_for(conditional, increment)

    def exitForVarStatement(self, ctx):
        self.exitForStatement(ctx)

    def exitForInStatement(self, ctx):
        self.exitForStatement(ctx)

    def exitForVarInStatement(self, ctx):
        self.exitForStatement(ctx)

    def exitWhileStatement(self, ctx):
        self.dialect.on_while(
            ctx.expressionSequence().getChild(0).getText())

    def exitIfStatement(self, ctx):
        self.dialect.on_if(
            ctx.expressionSequence().getChild(0).getText(),
            bool(ctx.Else())
        )

class JavaScriptDialect(Dialect):
    statements = None
    """
    A dictionary of statement types, each holding a list of tuples describing
    each instance.

    Types:
     function - Function declaration: (identifier, arguments string)
     for - For loop (conditional string, increment string)
     while - While loop (conditional string,)
     if - If (conditional string, has_else)
    """

    def __init__(self, filename, *args, **kwargs):
        self.lines = 0
        self.statements = { 'function': [],
                            'for': [],
                            'while': [],
                            'if': []}
        self.parse(filename)

    def get(self, statement_type, filter_fn = None):
        if filter_fn is None:
            return self.statements[statement_type]
        else:
            return list(filter(filter_fn, self.statements[statement_type]))

    def has(self, statement_type, filter_fn = None):
        return bool(self.get(statement_type, filter_fn))

    def on_function(self, identifier, arguments):
        self.statements['function'].append((identifier, arguments))

    def on_for(self, conditional, increment):
        self.statements['for'].append((conditional, increment))

    def on_while(self, conditional):
        self.statements['while'].append((conditional,))

    def on_if(self, conditional, has_else):
        self.statements['if'].append((conditional, has_else))

    def parse(self, code):
        lexer = ECMAScriptLexer(InputStream(code))
        parser = ECMAScriptParser(CommonTokenStream(lexer))
        listener = ScriptListener(self)
        walker = ParseTreeWalker()
        walker.walk(listener, parser.program())

    def has_seq(self):
        return self.lines > 1
    
    def has_if(self):
        return len(self.get('if')) > 0
    
    def has_ifelse(self):
        return len(self.get('if', lambda x: x[1])) > 0
    
    def has_for(self):
        return len(self.get('for')) > 0
    
    def has_while(self):
        return len(self.get('while')) > 0
