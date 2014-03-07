# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from whoosh.filedb.filestore import RamStorage
from whoosh.analysis import Tokenizer, Token, RegexTokenizer
from whoosh.fields import *
from whoosh import query
from whoosh.qparser import QueryParser

import lang

#TODO add more and more
greeting = u'''
招财进宝
生意兴隆
岁岁平安
和气生财
心想事成
万事如意
国家繁荣，人民祥和
财源广进
马到成功
升官发财
一路顺风
祝你新的一年快乐幸福
事业成功，家庭美满
新年快乐
恭祝新年吉祥，幸福和欢乐与你同在
'''

class WhooshGuess(object):
    def __init__(self):
        self.storage = RamStorage()
        schema = Schema(key=ID(stored=True), \
                ask=BOOLEAN(stored=True), \
                content=TEXT(stored=True, analyzer=RegexTokenizer()))
        self.ix = self.storage.create_index(schema)
        self.writer = self.ix.writer()
        self.is_train = False

        for s in greeting.split('\n'):
            self.train(u'matchinggreeting', s)
    
    @property
    def is_ok(self):
        return self.is_train

    def train(self, key, line):
        splits = u' '.join(list(lang.tokenizezh(line)))
        ask = lang.is_question(key)
        #print ask
        #print splits
        self.writer.add_document(key=key, content=splits, ask=ask)

    def train_ok(self):
        self.writer.commit(optimize=True)
        self.searcher = self.ix.searcher()
        self.parser = QueryParser("content", schema=self.ix.schema)
        self.is_train = True

    def guess(self, s, is_ask = None):
        assert(self.is_train)

        keys = list(lang.keyword(s))
        if len(keys) == 0:
            return ''
        
        # MUST contain the keys
        keys = u' '.join(keys)
        splits = u' '.join(list(lang.tokenizezh(s)))
        #q = self.parser.parse(splits + ' OR ' + keys)
        q1 = self.parser.parse(keys)
        q2 = self.parser.parse(splits)
        q = q1 | q2
        #print unicode(q)

        if not is_ask:
            ask = query.Term(u"ask", lang.is_question(s))
        else:
            ask = query.Term(u"ask", is_ask)
        results = self.searcher.search(q, filter=ask)
        for hit in results:
            return hit['key']
        return ''

def test_token(s):
    an = RegexTokenizer()
    for token in an(' '.join(list(lang.tokenizezh(s)))):
        print token.text, 
    print ''

def test_guess():
    sents = u'''
    你们什么时候开学
    我的书包在哪儿
    你怎么能这样
    你要去哪
    谁是那个小偷
    你是喝可乐还是啤酒
    你去呢还是我去
    你去还是我去
    游泳池里的人多不多
    这事是不是你干的
    那个笨蛋有没有钱
    我们明天爬山好不好
    你想去吗
    你愿意跟我在一起吗
    谁敲门
    他如何帮我搞定这个事情的
    你为什么要这样
    你这是为啥啊
    户外活动有哪些
    你哪去
    你为何如此
    那棵树多大
    你几岁
    你去哪儿
    你的车怎么了
    你去不去上海
    你有足够的钱没有
    电话呢
    背包呢
    你母亲多高
    他去不
    他走还是不走
    你说这宏不宏伟
    你们说这壮不壮观
    你这样做不好吧
    这事还能瞒得过他
    你饿了吧
    这个网站挺有意思啊
    下面开始是陈述句
    开始是陈述句
    地球很大
    他们跑足球
    你快走
    你走快点
    你走去那儿
    今天天气真冷
    这孩子多聪明啊
    你确实还是太笨了
    你干什么工作
    '''

    guess = WhooshGuess()
    for s in sents.split(u'\n'):
        if s.strip() != '':
            #test_token(s)
            guess.train(s.strip(), s)
    guess.train_ok()

    assert(u'你干什么工作' == guess.guess(u'你干什么工作'))
    assert(u'你干什么工作' == guess.guess(u'你做什么工作'))
    assert(u'' == guess.guess(u'你的车'))
    assert(u'你的车怎么了' == guess.guess(u'你车怎么了'))
    assert(u'' == guess.guess(u'你快'))
    assert(u'今天天气真冷' == guess.guess(u'天气真冷啊'))
    assert(u'' == guess.guess(u'是表达式'))
    assert(u'开始是陈述句' == guess.guess(u'是陈述句'))
    assert(u'开始是陈述句' == guess.guess(u'上面是陈述句'))
    assert(u'下面开始是陈述句' == guess.guess(u'下面是陈述句'))
    assert(u'下面开始是陈述句' == guess.guess(u'下面开始是陈述句'))
    assert(u'开始是陈述句' == guess.guess(u'上面开始是陈述句'))
    assert(u'今天天气真冷' == guess.guess(u'天气真冷啊'))

if __name__ == '__main__':
    test_guess()
