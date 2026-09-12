# -*- coding: utf-8 -*-
"""Підпис за варіантами відповідей (А--Д) для PDF і для бази."""
import re, sys, os
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)
from compare import norm

def canon(o):
    o = norm(o)
    o = o.replace(" ", "").replace(",", ".").replace("−", "-").replace("–", "-")
    o = re.sub(r"(см|дм|мм|км|м|грн|кг|г|год|хв|с)\d?$", "", o)
    o = re.sub(r"[^\w\u0400-\u04FF.+\-*/()\[\];|=<>]", "", o)
    return o

def base_options(raw):
    m = re.search(r"\\answerTable(?:Tall|Small)?((?:\{(?:[^{}]|\{[^{}]*\})*\}){5})", raw)
    if not m: return []
    args, depth, cur = [], 0, ""
    for ch in m.group(1):
        if ch == "{":
            depth += 1
            if depth == 1: cur = ""; continue
        if ch == "}":
            depth -= 1
            if depth == 0: args.append(cur); continue
        cur += ch
    return [canon(a) for a in args]

ABCD = re.compile(r"^\s*А\s+Б\s+В\s+Г\s+Д\s*$")
def pdf_options(text):
    lines = text.split("\n")
    for i, l in enumerate(lines):
        if ABCD.match(re.sub(r"\s+", " ", l)):
            rest = lines[i+1:i+3]
            parts = []
            for r in rest:
                p = [x for x in re.split(r"\s{3,}", r.strip()) if x]
                if len(parts) < 5 and len(p) >= 3: parts = p if not parts else parts
            if parts: return [canon(x) for x in parts][:5]
    return []

def opt_score(a, b):
    a = [x for x in a if x]; b = [x for x in b if x]
    if len(a) < 3 or len(b) < 3: return None
    sa, sb = set(a), set(b)
    return len(sa & sb) / max(1, min(len(sa), len(sb)))
