# -*- coding: utf-8 -*-
from matcher_parser import *

@generate
def macro_definition():
    yield lexeme(string('%'))
    macro_name = yield mstr
    yield lexeme(string('('))
    first = yield mstr.at_most(1)
    if len(first) == 1:
        rest = yield (comma >> mstr).many()
        rest.insert(0, first[0])
    else:
        rest = []
    yield lexeme(string(')'))

    yield lexeme(string('='))
    ast = yield choice
    yield lexeme(string(';')).times(0, 1)

    return {
        'name': macro_name,
        'parameters': rest,
        'ast': ast
    }

@generate
def macro_definitions():
    yield whitespace
    macro_definitions = yield macro_definition.many()
    return macro_definitions
