#!/usr/bin/env python
# -*- coding: utf-8 -*-

import re

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
    ws = ['']
    hz = False
    for c in q2b(s):
        if is_hz(c):
            ws.append(c)
            hz = True
        else:
            if c == ' ' and (ws[-1][-1] == ' ' or hz):
                continue
            if hz:
                ws.append(c)
                hz = False
            else:
                ws[-1] += c
    return ' '.join(ws)

def merge_zh(s):
    ws = ['']
    for w in s.split():
        if len(w) == 1 and is_hz(w[0]):
            ws[-1] += w
        else:
            ws.append(w)
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
    ss = u'_2005年我 们   出去玩2，_ 然后test  string hear聘情况！知道道理5abc如何走*。这么说不 *'
    print ss
    ss = split_zh(ss)
    print ss
    ss = u'ice to meet you,帅 哥'
    print merge_zh(ss)
