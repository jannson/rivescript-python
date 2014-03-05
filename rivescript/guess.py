# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from whoosh.filedb.filestore import RamStorage
from whoosh.analysis import Tokenizer, Token, RegexTokenizer
from whoosh.fields import *
from whoosh.qparser import QueryParser

import lang

class WhooshGuess(object):
    def __init__(self):
        self.storage = RamStorage()
        schema = Schema(key=TEXT(stored=True), \
                content=TEXT(stored=True, analyzer=RegexTokenizer()))
        self.ix = self.storage.create_index(schema)
        self.writer = self.ix.writer()

    def train(self, key, line):
        splits = ' '.join(list(lang.tokenizezh(line)))
        print splits
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
