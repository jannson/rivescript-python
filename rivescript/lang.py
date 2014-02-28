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

def split_zh(s):
    if s.strip() == '':
        return s

    ws = ['']
    hz = False
    for c in q2b(s):
        if is_hz(c):
            ws.append(c)
            hz = True
        else:
            if c == ' ' and (hz or (ws[-1] != '' and ws[-1][-1] == ' ')):
                continue
            if hz:
                ws.append(c)
                hz = False
            else:
                ws[-1] += c
    return ' '.join(ws)

ignore_pos = [u'不',u'没',u'未']
filter_pos = ['c','u','y']
def normal_zh(s):
    if s.strip() == '':
        return s

    words = []
    #for t in tagger.pos(tagger.cut(s)):
    for w in pseg.cut(s):
        t = (w.word, w.flag)
        #print t[0] + ' / ' + t[1]
        if any(t[1].find(fi) >= 0 for fi in filter_pos):
            continue
        elif t[1].find('d') >= 0 and all(t[0].find(ig) < 0 for ig in ignore_pos):
            continue
        else:
            words.append(t[0])
    return split_zh(' '.join(words))

no_en = re.compile(r'[^a-z0-9]')
def merge_zh(s):
    ws = []
    hz = ''
    for w in s.split():
        #if len(w) == 1 and is_hz(w[0]):
        if no_en.match(w):
            hz += w
        else:
            if hz != '':
                ws.append(hz)
                hz = ''
            ws.append(w)
    if hz != '':
        ws.append(hz)
    return ' '.join(ws)

# self-test
if __name__ == '__main__':
    samples = [
                (u'１２３４５６７８９０',u'1234567890'),
                (u'ａｂｃ１２３４５', u'abc12345'),
                (u'！＠＃％＾＆＊（）＿＋', u'!@#%^&*()_+'),
                (u'［］ＡＢＣＤＥＦＧＨＩＪＫ', u'[]ABCDEFGHIJK'),
                (u'㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩', u'㈠㈡㈢㈣㈤㈥㈦㈧㈨㈩'),
                (u'你啊，。。', u'你啊,..')
            ]

    for (key, value) in samples:
        if q2b(key) == value:
            print '%s:%s convert ok!' % (key, value)
        else:
            print '%s:%s convert failure!' % (key, value)
    ss = u'_2005年我 们,   出去玩2，_ 然后test  string hear聘情况！知道道理5abc如何走*。这么说不 *'
    print ss
    ss = split_zh(ss)
    print ss
    ss = u'帅 哥, ice to meet you, 帅 哥'
    print merge_zh(ss)
    ss = u'我们在这里，都值得你到这里，而且你的到来是我们的荣幸. 我的名字叫晟敢'
    print normal_zh(ss)
