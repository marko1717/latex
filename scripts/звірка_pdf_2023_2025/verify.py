# -*- coding: utf-8 -*-
"""Друга перевірка: дослівний фрагмент умови + набір варіантів."""
import json, re, os, sys, collections
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)
from compare import load_base, norm, words
from opts import pdf_options, base_options

TAIL = re.compile(r"(У завданнях\s+16.18|Розв.яжіть завдання\s+19.22|Завдання\s+1.15 мають|Одержані числові відповіді|Відповідь записуйте лише|Знак «мінус»|до кожного з трьох рядків)", re.I)
def statement(t):
    """текст умови без хвостових інструкцій сторінки"""
    m = TAIL.search(t)
    return t[:m.start()] if m else t

def wruns(t, k=3):
    """усі послідовності з k українських слів (>=4 літери) поспіль"""
    ws = re.findall(r"[а-яіїєґ']{4,}", norm(statement(t)))
    return [" ".join(ws[i:i+k]) for i in range(0, max(0, len(ws) - k + 1))]

def verify(base_texts, base_opts, t):
    runs = wruns(t)
    for r in runs:
        for i, bt in enumerate(base_texts):
            if r in bt: return "фраза", i
    po = [x for x in pdf_options(t) if x]
    if len(po) >= 3:
        for i, bo in enumerate(base_opts):
            if bo and len(set(po) & set(bo)) >= 3: return "варіанти", i
    return ("формула" if not runs else "немає"), None

if __name__ == "__main__":
    base = load_base()
    base_texts = [" ".join(re.findall(r"[а-яіїєґ']{4,}", norm(b["raw"]))) for b in base]
    base_opts = [base_options(b["raw"]) for b in base]
    m = json.load(open(S + "/matched.json", encoding="utf-8"))
    res = collections.Counter()
    for o in m:
        how, i = verify(base_texts, base_opts, o["text"])
        o["verify"] = how
        o["vtopic"] = base[i]["topic"] if i is not None else None
        o["vyear"] = base[i]["year"] if i is not None else None
        res[how] += 1
    json.dump(m, open(S + "/matched.json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("перевірка:", dict(res))
