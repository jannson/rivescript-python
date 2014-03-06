# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from whoosh.filedb.filestore import RamStorage
from whoosh.analysis import Tokenizer, Token, RegexTokenizer
from whoosh.fields import *
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
                content=TEXT(stored=True, analyzer=RegexTokenizer()))
        self.ix = self.storage.create_index(schema)
        self.writer = self.ix.writer()

        for s in greeting.split('\n'):
            self.train(u'matchinggreeting', s)

    def train(self, key, line):
        splits = u' '.join(list(lang.tokenizezh(line)))
        #print splits
        self.writer.add_document(key=key, content=splits)

    def train_ok(self):
        self.writer.commit(optimize=True)
        self.searcher = self.ix.searcher()
        self.parser = QueryParser("content", schema=self.ix.schema)

    def guess(self, s):
        splits = ' '.join(list(lang.tokenizezh(s)))
        q = self.parser.parse(splits)
        results = self.searcher.search(q)
        if len(results) == 0:
            return ''
        else:
            return results[0]['key']

def test_token(strs):
    an = RegexTokenizer()
    for s in strs:
        for token in an(' '.join(list(lang.tokenizezh(s)))):
            print token.text, 
        print ''

if __name__ == '__main__':
    guess = WhooshGuess()
    strs = [u'i love u too', u'i love u', u'我爱你', u'我爱我的祖国']
    print 'test token:'
    test_token(strs)
    
    print 'test query:'
    for s in strs:
        guess.train(s,s)
    guess.train_ok()
    print guess.guess(u'祖国')
    print guess.guess(u'事业成功')
