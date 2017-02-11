# -*- coding: utf-8 -*-

class ResponsePair:

    def __init__(self,
                 user_utterance_matcher,
                 scorer,
                 bot_utterance_generator):
        self.user_utterance_matcher = user_utterance_matcher
        self.scorer = scorer
        self.bot_utterance_generator = bot_utterance_generator

    def match(self, user_utterance, knowledge):
        return self.user_utterance_matcher(user_utterance, knowledge)

    def score(self, captured, context, knowledge):
        return self.scorer(captured, context, knowledge)

    def generate(self, captured, context, knowledge):
        return self.bot_utterance_generator(captured, context, knowledge)
