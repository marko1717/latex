# -*- coding: utf-8 -*-
"""LaTeX -> плаский рядок, подібний до того, що дає pdftotext (дроби «чисельник знаменник»)."""
import re, sys, os
S = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, S)

def _arg(s, i):
    """s[i]=='{' -> (вміст, індекс_після)"""
    d, j = 0, i
    while j < len(s):
        if s[j] == "\\": j += 2; continue
        if s[j] == "{": d += 1
        elif s[j] == "}":
            d -= 1
            if d == 0: return s[i+1:j], j+1
        j += 1
    return s[i+1:], len(s)

def flatten(t):
    t = re.sub(r"%[^\n]*", " ", t)
    t = re.sub(r"(?s)\\begin\{(tikzpicture|axis|nmtfit)\}.*?\\end\{\1\}", " ", t)
    t = re.sub(r"\\(?:displaystyle|left|right|limits|,|;|!|quad|qquad|;|\\)", " ", t)
    for a, b in [("\\cdot", "*"), ("\\times", "*"), ("\\pi", "π"), ("\\alpha", "a"), ("\\beta", "b"),
                 ("\\varphi", "f"), ("\\phi", "f"), ("\\infty", "8"), ("\\leqslant", "<="), ("\\geqslant", ">="),
                 ("\\le", "<="), ("\\ge", ">="), ("\\neq", "!="), ("\\circ", "°"), ("\\%", "%"), ("{,}", ",")]:
        t = t.replace(a, b)
    out, i = [], 0
    while i < len(t):
        m = re.match(r"\\(dfrac|frac|tfrac|sqrt|text|mathrm|mbox|textbf|textit|operatorname)\b", t[i:])
        if m:
            name = m.group(1); j = i + m.end()
            while j < len(t) and t[j] in " \n": j += 1
            if name in ("dfrac", "frac", "tfrac"):
                a1, j = _arg(t, j) if j < len(t) and t[j] == "{" else ("", j)
                while j < len(t) and t[j] in " \n": j += 1
                a2, j = _arg(t, j) if j < len(t) and t[j] == "{" else ("", j)
                out.append(" " + flatten(a1) + " " + flatten(a2) + " ")
            elif name == "sqrt":
                if j < len(t) and t[j] == "[":
                    k = t.index("]", j); deg = t[j+1:k]; j = k + 1
                else: deg = ""
                a1, j = _arg(t, j) if j < len(t) and t[j] == "{" else ("", j)
                out.append(" " + deg + "√" + flatten(a1) + " ")
            else:
                a1, j = _arg(t, j) if j < len(t) and t[j] == "{" else ("", j)
                out.append(" " + flatten(a1) + " ")
            i = j; continue
        if t[i] in "^_":
            j = i + 1
            if j >= len(t): break
            if t[j] == "{":
                a1, j = _arg(t, j); out.append(" " + flatten(a1) + " ")
            else:
                out.append(" " + t[j] + " "); j += 1
            i = j; continue
        if t[i] == "\\":
            m2 = re.match(r"\\([a-zA-Z]+)", t[i:])
            if m2:
                cmd = m2.group(1)
                if cmd in ("sin","cos","tg","ctg","lg","ln","log","arcsin","arccos","arctg","arcctg","tan","cot"):
                    out.append(" " + cmd + " ")
                i += m2.end(); continue
            i += 2; continue
        if t[i] in "${}&": i += 1; continue
        out.append(t[i]); i += 1
    s = "".join(out)
    s = s.replace("«", " ").replace("»", " ").replace("–", "-").replace("—", "-").replace("−", "-").replace("’", "'")
    return re.sub(r"\s+", " ", s).strip()

TOK = re.compile(r"[a-zA-Zα-ω°πα]|\d+(?:[.,]\d+)?|[+\-*/()=<>|√%]")
def tokens(s):
    s = s.lower().replace(",", ".")
    return TOK.findall(s)

def tok_sim(a, b):
    """схожість мультимножин математичних токенів"""
    import collections
    ca, cb = collections.Counter(tokens(a)), collections.Counter(tokens(b))
    if not ca or not cb: return 0.0
    inter = sum((ca & cb).values())
    return inter / max(sum(ca.values()), sum(cb.values()))
