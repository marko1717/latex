# -*- coding: utf-8 -*-
"""Каталог типів тестових завдань НМТ з алгебри: перевірка кожного зразка (правильний рівно один варіант,
пастки -- лише неправильні варіанти), рівномірні літери відповідей і запис у scripts/data/типи_алгебри_нмт.json.

Літери вирівнюються найменшою перестановкою: правильний варіант міняється місцями з тим, що стоїть на
потрібній літері; пастки задано номерами варіантів, тож їхні літери проставляються вже після перестановки.

    python3 scripts/типи_алгебри/зібрати.py && python3 scripts/типи_алгебри/pdf.py ВИХІД.pdf
"""
import os, sys, json, math, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
ВИХІД = os.path.join(os.path.dirname(HERE), "data", "типи_алгебри_нмт.json")
from спец import ТИПИ                                   # noqa: E402
from sympy import sympify, simplify, Set, N as num      # noqa: E402
L = "АБВГД"


def рівні(u, w):
    if isinstance(u, (str, tuple, frozenset)) or isinstance(w, (str, tuple, frozenset)): return u == w
    if isinstance(u, Set) or isinstance(w, Set): return u == w
    try:
        d = sympify(u) - sympify(w)
        if d == 0 or simplify(d) == 0: return True
        вільні = sorted(d.free_symbols, key=str)
        for p in ([0.37, 1.23, 2.71] if вільні else [None]):
            if abs(complex(num(d.subs({s: p for s in вільні}) if вільні else d, 30))) > 1e-9: return False
        return True
    except Exception:
        return False


def правильні(t):
    if "правильно" in t: return [i for i, o in enumerate(t["варіанти"]) if t["правильно"](o)]
    c = t["обч"]()
    return [i for i, o in enumerate(t["варіанти"]) if рівні(o, c)]


def цілі_літери(природні, фіксовані):
    """найменше переставлянь: природна літера лишається, доки її не забагато на цьому відрізку каталогу"""
    n, лічильник, ціль = len(природні), collections.Counter(), []
    for i, k in enumerate(природні):
        межа = math.ceil((i + 1) / 5) + 1
        if i in фіксовані or лічильник[k] + 1 <= межа:
            ціль.append(k)
        else:
            порядок = [(j + i) % 5 for j in range(5)]
            ціль.append(min(порядок, key=lambda j: (лічильник[j], порядок.index(j))))
        лічильник[ціль[-1]] += 1
    return ціль


def пастки_текст(пастки, σ):
    рядки = []
    for ключ, текст in пастки.items():
        idx = sorted(σ[k] for k in (ключ if isinstance(ключ, tuple) else (ключ,)))
        рядки.append((idx, ", ".join(L[k] for k in idx) + " -- " + текст))
    return "; ".join(r for _, r in sorted(рядки))


def таблиця(t, показ):
    вид = t.get("таблиця", "")
    if вид == "рисунки":
        клітинки = " & ".join(r"\vspace{3pt}\begin{nmtfit}%s\end{nmtfit}\vspace{2pt}" % p for p in показ)
        return ("\\par\\nopagebreak\\vspace{0.15cm}\\noindent\\begingroup\\setlength{\\tabcolsep}{2pt}\n"
                "\\begin{tabular}{|*{5}{>{\\centering\\arraybackslash}m{3.1cm}|}}\\hline\n"
                "\\rule[-0.15cm]{0pt}{0.6cm}\\textbf{А} & \\textbf{Б} & \\textbf{В} & \\textbf{Г} & \\textbf{Д} \\\\ \\hline\n"
                + клітинки + " \\\\ \\hline\n\\end{tabular}\\endgroup\\par\\vspace{0.25cm}")
    if вид == "список":
        рядки = " \\\\[0.25cm]\n".join(r"\textbf{%s} & %s" % (L[i], p) for i, p in enumerate(показ))
        return "\\par\\nopagebreak\\vspace{0.1cm}\\noindent\\begin{tabular}{@{}l@{\\quad}l@{}}\n" + рядки + "\n\\end{tabular}\\par\\vspace{0.25cm}"
    return ("\\answerTableTall" if вид == "Tall" else "\\answerTable") + "".join("{%s}" % p for p in показ)


def блок(t, показ):
    tab, рис = таблиця(t, показ), t.get("рисунок")
    if рис and t.get("розміщення") == "поруч" and t.get("таблиця") != "список":
        w = t.get("ширина", 0.55)
        return ("\\noindent\n\\begin{minipage}[c]{%.2f\\textwidth}\n\\zadnum %s\n\\end{minipage}\\hfill\n"
                "\\begin{minipage}[c]{%.2f\\textwidth}\\centering\n\\begin{nmtfit}%s\\end{nmtfit}\n\\end{minipage}\n"
                "\\par\\nbvspace{0.2cm}\n%s") % (w, t["умова"], 0.96 - w, рис, tab)
    if рис and t.get("розміщення") == "поруч":          # довгі варіанти списком -- ліворуч, рисунок праворуч
        w = t.get("ширина", 0.55)
        return ("\\zadtask{%s}\n\\noindent\n\\begin{minipage}[c]{%.2f\\textwidth}\n%s\n\\end{minipage}\\hfill\n"
                "\\begin{minipage}[c]{%.2f\\textwidth}\\centering\n\\begin{nmtfit}%s\\end{nmtfit}\n\\end{minipage}\\par\\vspace{0.2cm}") % (
                    t["умова"], w, tab, 0.96 - w, рис)
    if рис:
        return "\\zadtask{%s\\par\\nopagebreak\\vspace{0.15cm}\\begin{center}\\begin{nmtfit}%s\\end{nmtfit}\\end{center}}\n%s" % (t["умова"], рис, tab)
    return "\\zadtask{%s}\n%s" % (t["умова"], tab)


def main():
    природні = []
    for t in ТИПИ:
        assert len(t["показ"]) == 5 and len(t["варіанти"]) == 5, t["код"]
        h = правильні(t)
        assert len(h) == 1, (t["код"], "правильних варіантів: %s" % h)
        for ключ in t["пастки"]:
            assert h[0] not in (ключ if isinstance(ключ, tuple) else (ключ,)), (t["код"], "пастка на правильному варіанті")
        природні.append(h[0])
    фіксовані = {i for i, t in enumerate(ТИПИ) if t.get("фіксований")}
    ціль = цілі_літери(природні, фіксовані)
    out = []
    for t, k, g in zip(ТИПИ, природні, ціль):
        σ = list(range(5)); σ[k], σ[g] = g, k                 # старий номер -> новий
        order = sorted(range(5), key=lambda i: σ[i])          # новий порядок старих номерів
        t2 = dict(t, показ=[t["показ"][i] for i in order], варіанти=[t["варіанти"][i] for i in order])
        h = правильні(t2)
        assert h == [g], (t["код"], h, g)
        out.append(dict(код=t["код"], група=t["група"], назва=t["назва"], частота=t["частота"], формати=t["формати"], нмт=t["нмт"],
                        latex=блок(t2, t2["показ"]), відповідь=L[g], пастки=пастки_текст(t["пастки"], σ), переставлено=k != g))
    json.dump([{k: v for k, v in r.items() if k != "переставлено"} for r in out], open(ВИХІД, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("усі %d зразків: рівно один правильний варіант, пастки -- лише на неправильних" % len(out))
    print("природні літери:", dict(sorted(collections.Counter(L[k] for k in природні).items())))
    print("після вирівнювання:", dict(sorted(collections.Counter(r["відповідь"] for r in out).items())),
          "| переставлено варіантів у %d типах" % sum(r["переставлено"] for r in out))
    print("послідовність:", "".join(r["відповідь"] for r in out))


if __name__ == "__main__":
    main()
