# -*- coding: utf-8 -*-

from .matcher_parser import matcher as matcher_parser
import marisa_trie

class MatcherBuilder:

    def __init__(self,
                 ontology={},
                 macros=[],
                 phrases={}):
        self.ontology = ontology
        self.macros = macros
        self.phrases = phrases
        self.phrases_trie = marisa_trie.Trie(phrases.keys())

    def build(self, source):
        ast = matcher_parser.parse(source)
        ast = self.ast_prepare(ast)

        def matcher(user_utterance, knowledge):
            return self.match(ast, user_utterance)

        return matcher # (user_utterance, knowledge) => match_result

    def ast_prepare(self, ast, bindings=None, no_phrase_expansion=False):
        if bindings is None:
            bindings = {
                'empty': {'type': 'text', 'text': ''}
            }

        if ast['type'] == 'sequence':
            return {
                'type': 'sequence',
                'elements': [self.ast_prepare(element, bindings, no_phrase_expansion)
                             for element in ast['elements']]
            }
        elif ast['type'] == 'choice':
            return {
                'type': 'choice',
                'elements': [self.ast_prepare(element, bindings, no_phrase_expansion)
                             for element in ast['elements']]
            }
        elif ast['type'] == 'text':
            if no_phrase_expansion:
                return ast

            text = ast['text']
            elements = []
            i = j = 0
            while j < len(text):
                prefixes = self.phrases_trie.prefixes(text[j:])
                if len(prefixes) > 0:
                    prefixes.sort(key=len, reverse=True)
                    phrase_key = prefixes[0]
                    if i < j:
                        elements.append({
                            'type': 'text',
                            'text': text[i:j]
                        })
                    elements.append(self.ast_prepare(self.phrases[phrase_key], bindings, True))
                    i = j = j + len(phrase_key)
                else:
                    j += 1
            if i < j:
                elements.append({
                    'type': 'text',
                    'text': text[i:j]
                })
            if len(elements) == 1:
                return elements[0]
            else:
                return {
                    'type': 'sequence',
                    'elements': elements
                }
        elif ast['type'] == 'macro':
            elements = []
            arguments = [self.ast_prepare(argument, bindings, no_phrase_expansion) for argument in ast['arguments']]
            for macro in self.macros:
                if macro['name'] == ast['name'] and len(macro['parameters']) == len(ast['arguments']):
                    new_bindings = dict(zip(macro['parameters'], arguments))
                    new_bindings.update(bindings)
                    elements.append(self.ast_prepare(macro['ast'], new_bindings, no_phrase_expansion))
            if len(elements) == 1:
                return elements[0]
            else:
                return {
                    'type': 'choice',
                    'elements': elements
                }
        elif ast['type'] == 'ref':
            return bindings[ast['name']]
        return ast

    def match(self, ast, text):
        branches = [([ast], text, [])]

        while branches:
            thunk, text, captured = branches.pop(0)
            if not thunk:
                if len(text) == 0:
                    return dict(captured)
                else:
                    continue
            ast = thunk.pop()

            if ast['type'] == 'sequence':
                thunk.extend(reversed(ast['elements']))
                branches.append((thunk, text, captured))
            elif ast['type'] == 'choice':
                for element in reversed(ast['elements']):
                    branches.append((thunk + [element], text, captured))
            elif ast['type'] == 'text':
                if text.startswith(ast['text']):
                    branches.append((thunk, text[len(ast['text']):], captured))
            elif ast['type'] == 'entity':
                instance =  self.match_entity(ast['name'], text)
                if instance:
                    text = text[len(instance['raw']):]
                    if ast['label'] is not None:
                        captured = captured + [(ast['label'], instance)]
                    branches.append((thunk, text, captured))
            elif ast['type'] == 'any':
                if ast.get('label'):
                    capture_item = (ast['label'], ast.get('capture', ''))
                    branches.append((thunk, text, captured + [capture_item]))
                else:
                    branches.append((thunk, text, captured))
                if len(text) > 0:
                    new_any = {
                        'type': 'any',
                        'label': ast.get('label'),
                        'capture': ast.get('capture', '') + text[0]
                    }
                    branches.append((thunk + [new_any], text[1:], captured))

    def match_entity(self, entity, text):
        if entity not in self.ontology:
            return
        for child in self.ontology[entity]:
            if child.startswith('#'):
                result = self.match_entity(child, text)
                if result:
                    return result
            else:
                if text.startswith(child):
                    return {
                        'entity': entity,
                        'raw': child
                    }
