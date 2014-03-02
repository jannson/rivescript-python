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
    rstring = ""
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

def normal_zh(ins):
    if ins.strip() == '':
        return ins
    s = q2b(ins)
    return merge_zh(s)

ignore_pos = [u'不',u'没',u'未']
filter_pos = ['c','u','y', 'z']

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
    
class Tokenizer:
    def tokenize(self, text):
        for w in pseg.cut(text):
            yield w.word
            
def normal_pos(ins):
    if ins.strip() == '':
        return ins
    s = q2b(ins)

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
            #print t[0] + ' / ' + t[1]
            #print any(t[1].find(fi) >= 0 for fi in filter_pos) 
            if any(t[1].find(fi) >= 0 for fi in filter_pos) \
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
    #print normal_pos(s)
    assert(u'是谁'== normal_pos(s))

# self-test
if __name__ == '__main__':
    test_merge_zh()
    test_pos()