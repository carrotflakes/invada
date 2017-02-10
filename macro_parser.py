# -*- coding: utf-8 -*-
from matcher_parser import *

@generate
def macro_definition():
    yield lexeme(string('%'))
    macro_name = yield mstr
    yield lexeme(string('('))
    first = yield mstr
    rest = yield (comma >> mstr).many()
    yield lexeme(string(')'))
    rest.insert(0, first)

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
