#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re
#from crfseg import Tagger
import jieba.posseg as pseg

#tagger = Tagger()

def is_hz(c):
    # http://www.iteye.com/topic/558050

    r = [
        # 标准CJK文字
        (0x3400, 0x4DB5), (0x4E00, 0x9FA5), (0x9FA6, 0x9FBB), (0xF900, 0xFA2D),
        (0xFA30, 0xFA6A), (0xFA70, 0xFAD9), (0x20000, 0x2A6D6), (0x2F800, 0x2FA1D),
        # 全角ASCII、全角中英文标点、半宽片假名、半宽平假名、半宽韩文字母
        (0xFF00, 0xFFEF),
        # CJK部首补充
        (0x2E80, 0x2EFF),
        # CJK标点符号
        (0x3000, 0x303F),
        # CJK笔划
        (0x31C0, 0x31EF)]
    return any(s <= ord(c) <= e for s, e in r)

#TODO do better for this
def is_en(c):
    r = [('0','9'), ('A','Z'), ('a','z'), ('=','='), ('/','/')]
    return any(ord(s) <= ord(c) <= ord(e) for s, e in r)

def q2b(ustring):
    rstring = u""
    for uchar in ustring:
        inside_code = ord(uchar)
        # 全角字符unicode编码从65281~65374 （十六进制 0xFF01 ~ 0xFF5E）
        # 半角字符unicode编码从33~126 （十六进制 0x21~ 0x7E）
        # 而且除空格外,全角/半角按unicode编码排序在顺序上是对应的
        if inside_code == 0x3000:
            # 空格 全角为0x3000 半角为0x0020
            inside_code = 0x0020
        elif inside_code == 0x3002:
            # 中文句号
            inside_code = 0x2e
        else:
            inside_code -= 0xfee0
        if inside_code < 0x0020 or inside_code > 0x7e:
            rstring += uchar
        else:
            rstring += unichr(inside_code)
    return rstring

def sentences(s):
    if isinstance(s, str):
        s = s.decode('utf-8')
    s = q2b(s)

    pos = 0
    sentenceList = []
    l = len(s)
    while pos < l:
        try: p = s.index('.', pos)
        except: p = l+1
        try: q = s.index('?', pos)
        except: q = l+1
        try: e = s.index('!', pos)
        except: e = l+1
        try: f = s.index('~', pos)
        except: f = l+1
        end = min(p,q,e,f)
        if end == e:
            sentenceList.append( (s[pos:end].strip(), True) )
        else:
            sentenceList.append( (s[pos:end].strip(), False) )
        pos = end+1
    # If no sentences were found, return a one-item list containing
    # the entire input string.
    if len(sentenceList) == 0: sentenceList.append( (s,None) )
    sens = []
    for ins, ask in sentenceList:
        s = re.sub(ur'(?u)\W+', ' ', ins, re.U)
        sens.append( (s, ask) )
    return sens

def normal_zh(ins):
    if ins.strip() == '':
        return ins
    #s = q2b(ins)
    s = ins
    return merge_zh(s)

reserve_pos = [u'n', u'v']
ignore_pos = [u'不',u'没',u'未']
filter_pos = ['c','u','y','z','e']

def find_zh(s):
    tmp = s[0]
    hz = is_hz(s[0])
    for w in s[1:]:
        if is_hz(w):
            if hz:
                tmp += w
            else:
                if tmp != '':
                    yield tmp, False
                hz = True
                tmp = w
        else:
            if not hz:
                tmp += w
            else:
                if tmp != '':
                    yield tmp, True
                hz = False
                tmp = w
    yield tmp, hz

#filter_pos2 = ['c','u','y','z','r','x','m']
reserve_pos2 = [u'n', u'eng', u's']
def tokenizezh(text):
    for w in pseg.cut(text):
        if w.word.strip() != '' and (any(w.flag.find(fi) >= 0 for fi in reserve_pos) \
            or (not any(w.flag.find(fi) >= 0 for fi in filter_pos))):
            yield w.word.lower()

def keyword(text):
    for w in pseg.cut(text):
        if w.word.strip() != '' and \
             ( any(w.flag.find(fi) >= 0 for fi in reserve_pos2) \
                    or any(w.word.find(fi) >= 0 for fi in [u'我', u'你', u'他']) ):
                yield w.word.lower()

class Tokenizer:
    def tokenize(self, text):
        for w in tokenizezh(text):
            yield w

def normal_pos(ins):
    if ins.strip() == '':
        return ins
    #s = q2b(ins)
    s = ins

    words = ['']
    for seg, zh in find_zh(s):
        #seg = zh_s.strip()
        if seg == '':
            continue
        if not zh:
            words.append(seg)
            continue
        for w in pseg.cut(seg):
            t = (w.word, w.flag)
            if any(t[1].find(fi) >= 0 for fi in reserve_pos):
                words.append(t[0])
            elif any(t[1].find(fi) >= 0 for fi in filter_pos) \
                    or (t[1].find('d') >= 0 and all(t[0].find(ig) < 0 for ig in ignore_pos)):
                #if words[-1] == ' ':
                #    continue
                #else:
                #    words.append(' ')
                #print w
                continue
            else:
                words.append(t[0])
    #print 'BEGPOS', ''.join(words), 'END'
    return merge_zh(''.join(words))

def merge_zh(s):
    rlt = ''
    i = 0
    l = len(s)
    while i < l:
        if not is_hz(s[i]):
            rlt += s[i]
            i += 1
            continue
        rlt += s[i]
        i += 1
        is_space = False
        while i < l and s[i] == ' ':
            i += 1
            is_space = True
        if is_space and i < l and not is_hz(s[i]):
            rlt += ' '
    return re.sub('\s+', ' ', rlt.strip())

def test_merge_zh():
    s = u'然后  出去 工作了 '
    assert(u'然后出去工作了' == merge_zh(s))

    s = u'abc  然后 just 出去  test  工作it了 '
    assert(u'abc 然后 just 出去 test 工作it了' == merge_zh(s))

    s = u'然后just   test出 去it了'
    assert(u'然后just test出去it了' == merge_zh(s))

def test_pos():
    s = u'是谁呢'
    assert(u'是谁'== normal_pos(s))
    s = u'你会讲英语吗'
    assert(u'你会讲英语' == normal_pos(s))
    s = u'_2005年我们出去玩2，_ 然后聘情况！知道道理5abc如何走*。这么说不 *'
    print list(pseg.cut(s))
    s = u'户外活动有哪些'
    print list(pseg.cut(s))
    s = u'知道这条路怎么走吗'
    print list(pseg.cut(s))
    s = u'小突想知道这条路怎么走'
    print list(pseg.cut(s))

'''
def test_tokenzh():
    s = u'你是谁呢'
    assert(u'是' == u''.join(list(tokenizezh(s))))
    s = u'你会讲英语吗'
    assert(u'会讲英语' == u''.join(list(tokenizezh(s))))
    s = u'can you speak eng, 能吗'
    #print "BEGIN:"+u' '.join(list(tokenizezh(s)))+":END"
    assert(u'can you speak eng 能' == u' '.join(list(tokenizezh(s))))
    s = u'户外活动有哪些'
    assert(u'户外活动有' == u''.join(list(tokenizezh(s))))
'''

def test_sens():
    sents = sentences("First.  Second, still?  Third and Final!  Well, not really")
    print sents
    sents = sentences(u'_2005年我们出去玩2，_ 然后聘情况！知道道理5abc如何走*。这么说不 *')
    for s in sents:
        print s, ' / ',

questions_pos = set([u'什么r', u'哪儿r', u'哪r', u'怎么r', u'如何r', u'为什么r',\
        u'为啥r', u'为何r', u'谁r', u'吗y', u'呢y'])

def is_question(s):
    s = s.strip()
    if s == '':
        return False

    cuts = list(pseg.cut(s))
    pos = [w.word+w.flag for w in cuts]
    words = [w.word for w in cuts]
    pos_set = set(pos)
    #print u' '.join(pos)
    
    if u'是v' in pos_set and u'还是c' in pos_set:
        return True

    if pos[-1] == u'不d':
        return True

    if len(pos_set & questions_pos) > 0:
        return True

    for x in pos:
        if x[-1] == u'r' and any(x.find(fi) >= 0 for fi in [u'为', u'什么', u'哪']):
            return True
        if x[-1] == u'l' and x.find(u'什么') >= 0:
            return True

    sel = next((x for x in range(len(pos)) if pos[x] in [u'不d',u'还是c']), 0)
    if sel > 0:
        p1, p2 = set(pos[0:sel]), set(pos[sel+1:])
        if len(p1 & p2) > 0:
            return True

    # Now remove all "r"s
    pos = [w.word+w.flag for w in cuts if w.flag != 'r']
    words = [w.word for w in cuts if w.flag != 'r']

    sel = next((x for x in range(len(words)) if words[x] in [u'不',u'没']), 0)
    if sel > 0 and words[sel-1] == words[sel+1]:
        return True

    sel = s.find(u'不')
    if sel <= 0:
        sel = s.find(u'没')
    if sel > 0 and s[:sel].find(s[sel+1]) >= 0:
        return True

    sel = 0
    for x in pos:
        if len(set([u'多',u'几']) & set(x)) > 0:
            if len(x) == 2 and pos[-1][-1] == 'a':
                return True
            if len(x) > 2 and x[-1] == 'm':
                return True
        sel += 1

    return False
        
def ask_sents():
    asks = u'''
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
    你多少岁了
    你干什么工作
    '''
    
    no_asks = u'''
    你这样做不好吧
    这事还能瞒得过他
    你饿了吧
    这个网站挺有意思啊
    下面开始是陈述句
    地球很大
    他们跑足球
    你快走
    你走快点
    你走去那儿
    今天天气真冷
    这孩子多聪明啊
    你确实还是太笨了
    '''
    #你是什么东西 assert error hear
    #我哪儿也不去

    for s in asks.split(u'\n'):
        if s.strip() != '':
            assert(is_question(s.strip()))

    for s in no_asks.split(u'\n'):
        if s.strip() != '':
            assert(not is_question(s.strip()))

# self-test
if __name__ == '__main__':
    test_merge_zh()
    test_pos()
    #test_tokenzh()
    #test_sens()
    ask_sents()

