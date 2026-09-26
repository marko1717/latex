# -*- coding: utf-8 -*-
"""Каталог типів рівнянь, систем і нерівностей НМТ: перестановка варіантів (рівномірні літери відповідей),
перевірка кожного зразка (рівно один правильний варіант) і запис у scripts/data/типи_рівнянь_нмт.json.

    python3 scripts/типи_рівнянь/зібрати.py && python3 scripts/типи_рівнянь/pdf.py ВИХІД.pdf
"""
import os, sys, re, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ВИХІД = os.path.join(os.path.dirname(HERE), "data", "типи_рівнянь_нмт.json")
from спец import ТИПИ
from sympy import FiniteSet, Set, Interval, Union, EmptySet, nsimplify, N, simplify
L='АБВГД'
ПЕРЕСТАНОВКИ = {'А5':[4,1,3,0,2], 'А13':[3,1,0,4,2], 'Б1':[2,3,0,4,1], 'В2':[4,1,3,0,2],
                'В4':[2,1,4,0,3], 'Г2':[3,0,4,2,1], 'Г6':[2,4,0,3,1], 'В7':[2,1,0,3,4], 'А4':[1,3,2,4,0], 'В9':[0,1,2,4,3]}

def args_таблиці(s):
    m=re.search(r'\\answerTable(Tall)?', s); i=m.end(); out=[]
    for _ in range(5):
        assert s[i]=='{', s[i:i+20]
        d=0; j=i
        while True:
            if s[j]=='{': d+=1
            elif s[j]=='}':
                d-=1
                if d==0: break
            j+=1
        out.append(s[i+1:j]); i=j+1
    return m.start(), i, m.group(0), out

def чисто(c):
    def f(e):
        try: return simplify(e) if e.is_number and e.is_finite else e
        except Exception: return e
    if isinstance(c, Interval): return Interval(f(c.start), f(c.end), c.left_open, c.right_open)
    if isinstance(c, Union): return Union(*[чисто(a) for a in c.args])
    if isinstance(c, FiniteSet): return FiniteSet(*[f(a) if not isinstance(a, tuple) else a for a in c])
    return c

def рівні(a,b):
    return (a - b) == EmptySet and (b - a) == EmptySet

def правильні(t):
    o=t['варіанти']; вид=t['вид']; c=t['перевірка']()
    if вид=='множина': c=чисто(c)          # кінці проміжків на кшталт 2-log(9)/log(3) -> 0
    if вид=='значення': return [i for i,v in enumerate(o) if any(simplify(v-w)==0 for w in c)]
    if вид=='множина': return [i for i,v in enumerate(o) if isinstance(v,Set) and рівні(v,c)]
    if вид=='проміжок кореня': r=list(c)[0]; return [i for i,v in enumerate(o) if r in v]
    if вид=='пара': return [i for i,v in enumerate(o) if any(tuple(v)==tuple(w) for w in c)]
    if вид=='число-розвʼязок': return [i for i,v in enumerate(o) if v in c]

out=[]
for t in ТИПИ:
    t=dict(t)
    p=ПЕРЕСТАНОВКИ.get(t['код'])
    if p:
        a,b,macro,args=args_таблиці(t['latex'])
        t['latex']=t['latex'][:a]+macro+''.join('{%s}'%args[k] for k in p)+t['latex'][b:]
        t['варіанти']=[t['варіанти'][k] for k in p]
        new_of_old={L[old]:L[new] for new,old in enumerate(p)}
        t['пастки']=re.sub(r'(?<![А-Яа-яІіЇїЄєҐґ])([АБВГД])(?![А-Яа-яІіЇїЄєҐґ])', lambda m:new_of_old[m.group(1)], t['пастки'])
    h=правильні(t)
    assert len(h)==1, (t['код'], h)
    t['відповідь']=L[h[0]]
    out.append(t)
print('усі %d зразків: рівно один правильний варіант' % len(out))
print('розподіл відповідей:', dict(sorted(collections.Counter(t['відповідь'] for t in out).items())))
for t in out:
    if t['код'] in ПЕРЕСТАНОВКИ: print('  %-4s -> %s | %s' % (t['код'], t['відповідь'], t['пастки'][:90]))
json.dump([{k:v for k,v in t.items() if k in ('код','група','назва','частота','формати','нмт','latex','відповідь','пастки')} for t in out],
          open(ВИХІД,'w',encoding='utf-8'), ensure_ascii=False, indent=1)
