# -*- coding: utf-8 -*-

from invada import matcher_parser, macro_definitions_parser, MatcherBuilder, ResponsePair, Engine

ontology = {
    '#果物': {'#りんご', '#みかん', '#ぶどう'},
    '#りんご': {'林檎', 'りんご', 'リンゴ'},
    '#みかん': {'蜜柑', 'みかん', 'ミカン'},
    '#ぶどう': {'葡萄', 'ぶどう', 'ブドウ'},
}

macros = macro_definitions_parser.parse('''
%twice(a) = $a $a ;
%tell_me(a) = $a について教えて|$a を教えて|$a 教えて|$a って何|$a って何? ;
%color() = 赤 | 青 | 黄 ;
''')

traps = {
    '?': matcher_parser.parse('? | ？'),
    '何': matcher_parser.parse('何 | なに'),
    '私': matcher_parser.parse('私 | わたし'),
    '名前': matcher_parser.parse('名前 | なまえ'),
}


def merge(source, target):
    for key in source:
        if key not in target:
            target[key] = source[key]
    return target

raw_response_pairs = [
    ('こんにちは',
     lambda captured, context, knowledge: 1,
     lambda captured, context, knowledge: ('こんちゃーす', context)),
    ('こんにちは',
     lambda captured, context, knowledge: 2 if 'name' in context else 0,
     lambda captured, context, knowledge:
     ('{}さんこんちゃーす'.format(context['name']), context)),
    ('#果物@果物 が好きです',
     lambda captured, context, knowledge: 1,
     lambda captured, context, knowledge: ('{}好きなんだ'.format(captured['果物']['raw']), context)),
    ('%twice(こんにちは)',
     lambda captured, context, knowledge: 1,
     lambda captured, context, knowledge: ('はまちちゃんかな？', context)),
    ('%twice(あ)',
     lambda captured, context, knowledge: 1,
     lambda captured, context, knowledge: ('ああ？', context)),
    ('%tell_me(#果物@果物)',
     lambda captured, context, knowledge: 1,
     lambda captured, context, knowledge: ('{}は{}よ'.format(captured['果物']['raw'], knowledge['果物'][captured['果物']['entity']]), context)),
    ('%color()',
     lambda captured, context, knowledge: 1,
     lambda captured, context, knowledge: ('色ですか？', context)),
    ('私の名前は *@name です',
     lambda captured, context, knowledge: 1,
     lambda captured, context, knowledge:
     ('{}さんですね！'.format(captured['name']),
      merge(context, {'name': captured['name']}))),
    ('*',
     lambda captured, context, knowledge: 0.01,
     lambda captured, context, knowledge: ('えっ？', context)),
]

knowledge = {
    '果物': {
        '#りんご': '赤くて丸い',
        '#みかん': 'いろんな種類がある',
        '#ぶどう': 'ワインの原料だ',
    }
}


if __name__ == '__main__':

    matcher_builder = MatcherBuilder(ontology, macros, traps)

    def make_response_pair(raw_response_pair):
        matcher, scorer, generator = raw_response_pair
        return ResponsePair(matcher_builder.build(matcher),
                            scorer,
                            generator)

    response_pairs = [make_response_pair(raw_response_pair)
                      for raw_response_pair in raw_response_pairs]

    engine = Engine(response_pairs, knowledge=knowledge)

    context = {}

    print('いらっしゃいませ！')
    while True:
        user_utterance = input()
        bot_utterance, context = engine.chat(user_utterance, context)
        print(bot_utterance)
