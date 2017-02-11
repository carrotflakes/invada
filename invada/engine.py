# -*- coding: utf-8 -*-


class Engine:

    def __init__(self,
                 response_pairs,
                 knowledge={}):
        self.response_pairs = response_pairs
        self.knowledge = knowledge

    def chat(self, user_utterance, context):
        best_score = 0
        best_response_pair = None
        best_captured = {}
        for response_pair in self.response_pairs:
            captured = response_pair.match(user_utterance, self.knowledge)

            if captured is None:
                continue

            score = response_pair.score(captured, context, self.knowledge)

            if best_score < score:
                best_score, best_response_pair, best_captured = score, response_pair, captured

        return best_response_pair.generate(best_captured, context, self.knowledge)
