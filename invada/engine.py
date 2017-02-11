# -*- coding: utf-8 -*-

from response_pair import ResponsePair


default_response_generator = lambda captured, context, knowledge: ('', context)


class Engine:

    def __init__(self,
                 response_pairs,
                 default_response_generator=default_response_generator,
                 knowledge={}):
        self.response_pairs = response_pairs
        self.default_response_pairs = ResponsePair(None, None, default_response_generator)
        self.knowledge = knowledge

    def chat(self, user_utterance, context):
        best_score = 0
        best_response_pair = self.default_response_pairs
        best_captured = {}
        for response_pair in self.response_pairs:
            captured = response_pair.match(user_utterance, self.knowledge)

            if captured is None:
                continue

            score = response_pair.score(captured, context, self.knowledge)

            if best_score < score:
                best_score, best_response_pair, best_captured = score, response_pair, captured

        return best_response_pair.generate(best_captured, context, self.knowledge)
