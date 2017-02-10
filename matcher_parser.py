# -*- coding: utf-8 -*-
from parsy import string, regex, generate
import re


whitespace = regex(r'\s*', re.MULTILINE)

lexeme = lambda p: p << whitespace

comma  = lexeme(string(','))
pipe  = lexeme(string('|'))

mstr_part = regex(r'[^%$#@,|()\s\\]+')
mstr_esc = string('\\') >> (
  string('\\')
  | string('/')
  | regex(r'[%$#@,|()\s]')
  | string('b').result('\b')
  | string('f').result('\f')
  | string('n').result('\n')
  | string('r').result('\r')
  | string('t').result('\t')
  | regex(r'u[0-9a-fA-F]{4}').map(lambda s: chr(int(s[1:], 16)))
)

mstr = lexeme((mstr_part | mstr_esc).at_least(1).map(''.join))


@generate
def text():
    text = yield mstr
    return {
        'type': 'text',
        'text': text
    }

@generate
def entity():
    yield string('#')
    entity_name = yield mstr
    return {
        'type': 'entity',
        'name': '#' + entity_name,
        'label': None
    }

@generate
def labeledEntity():
    yield string('#')
    entity_name = yield mstr
    yield lexeme(string('@'))
    label = yield mstr
    return {
        'type': 'entity',
        'name': '#' + entity_name,
        'label': label
    }

@generate
def macro():
    yield lexeme(string('%'))
    macro_name = yield mstr
    yield lexeme(string('('))
    first = yield sequence
    rest = yield (comma >> sequence).many()
    yield lexeme(string(')'))
    rest.insert(0, first)
    return {
        'type': 'macro',
        'name': macro_name,
        'arguments': rest
    }

@generate
def ref():
    yield string('$')
    ref_name = yield mstr
    return {
        'type': 'ref',
        'name': ref_name
    }

@generate
def paren():
    yield lexeme(string('('))
    element = yield choice
    yield lexeme(string(')'))
    return element

@generate
def sequence():
    elements = yield (text | macro | labeledEntity | entity | ref | paren).at_least(1)
    if len(elements) == 1:
        return elements[0]
    return {
        'type': 'sequence',
        'elements': elements
    }

@generate
def choice():
    first = yield sequence
    rest = yield (pipe >> sequence).many()
    if len(rest) == 0:
        return first
    rest.insert(0, first)
    return {
        'type': 'choice',
        'elements': rest
    }

parser = whitespace >> choice


if __name__ == '__main__':
    print(parser.parse('ええと、 %tell_me(#果物@果物) | #果物 (教えて|テルミー)'))
    print(parser.parse('$a $b'))
    print(parser.parse('\@\%\(\)'))
