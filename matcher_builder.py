# -*- coding: utf-8 -*-

from matcher_parser import matcher as matcher_parser
import marisa_trie

class MatcherBuilder:

    def __init__(self,
                 ontology={},
                 macros=[],
                 traps={}):
        self.ontology = ontology
        self.macros = macros
        self.traps = traps
        self.traps_trie = marisa_trie.Trie(traps.keys())

    def build(self, source):
        ast = matcher_parser.parse(source)
        ast = self.ast_prepare(ast)

        def matcher(user_utterance, knowledge):
            result = self.match(ast, user_utterance, {})
            if result and len(result[0]) == 0:
                return result[1]

        return matcher # (user_utterance, knowledge) => match_result

    def ast_prepare(self, ast, bindings={}):
        if ast['type'] == 'sequence':
            ast['elements'] = [self.ast_prepare(element, bindings)
                               for element in ast['elements']]
        if ast['type'] == 'choice':
            ast['elements'] = [self.ast_prepare(element, bindings)
                               for element in ast['elements']]
        elif ast['type'] == 'text':
            text = ast['text']
            elements = []
            i = j = 0
            while j < len(text):
                prefixes = self.traps_trie.prefixes(text[j:])
                if len(prefixes) > 0:
                    prefixes.sort(key=len, reverse=True)
                    trap_key = prefixes[0]
                    if i < j:
                        elements.append({
                            'type': 'text',
                            'text': text[i:j]
                        })
                    elements.append(self.traps[trap_key])
                    i = j = j + len(trap_key)
                else:
                    j += 1
            if i < j:
                elements.append({
                    'type': 'text',
                    'text': text[i:j]
                })
            if len(elements) != 1:
                ast = {
                    'type': 'sequence',
                    'elements': elements
                }
        elif ast['type'] == 'macro':
            elements = []
            arguments = [self.ast_prepare(argument, bindings) for argument in ast['arguments']]
            for macro in self.macros:
                if macro['name'] == ast['name'] and len(macro['parameters']) == len(ast['arguments']):
                    new_bindings = dict(zip(macro['parameters'], arguments))
                    new_bindings.update(bindings)
                    elements.append(self.ast_prepare(macro['ast'], new_bindings))
            if len(elements) == 1:
                ast = elements[0]
            else:
                ast = {
                    'type': 'choice',
                    'elements': elements
                }
        elif ast['type'] == 'ref':
            ast = bindings[ast['name']]
        return ast

    def match(self, ast, text, captured):
        if ast['type'] == 'sequence':
            for element in ast['elements']:
                result = self.match(element, text, captured)
                if not result:
                    return None
                text, captured = result
            return text, captured
        if ast['type'] == 'choice':
            for element in ast['elements']:
                result = self.match(element, text, captured)
                if result:
                    captured.update(result[1])
                    return result[0], captured
            return None
        elif ast['type'] == 'text':
            if ast['text'] == text[:len(ast['text'])]:
                return text[len(ast['text']):], captured
            return None
        elif ast['type'] == 'entity':
            instance =  self.match_entity(ast['name'], text)
            if instance:
                text = text[len(instance['raw']):]
                if ast['label'] is not None:
                    captured[ast['label']] = instance
                return text, captured

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
