# -*- coding: utf-8 -*-
"""Спільний збирач каталогів типів НМТ (scripts/типи_*): перевірка кожного зразка (правильний рівно один варіант,
пастки -- лише на неправильних), рівномірні літери відповідей і LaTeX-блок завдання.

Літери вирівнюються найменшою перестановкою: правильний варіант міняється місцями з тим, що стоїть на
потрібній літері; пастки задано номерами варіантів, тож їхні літери проставляються вже після перестановки.
Завдання на відповідність (1--3 і А--Д) -- зібрати_відповідності: кожному пункту рівно один варіант, відповіді різні.
Завдання з короткою відповіддю -- зібрати_відкриті: відповідь для бланка НМТ, типові хибні відповіді обчислено."""
import json, math, re, collections
from decimal import Decimal
from sympy import sympify, simplify, Set, Rational, N as num
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


def рисунки_АД(рисунки):
    """п'ять рисунків у таблиці з літерами А--Д (варіанти-рисунки)"""
    клітинки = " & ".join(r"\vspace{3pt}\begin{nmtfit}%s\end{nmtfit}\vspace{2pt}" % p for p in рисунки)
    return ("\\begingroup\\setlength{\\tabcolsep}{2pt}\n\\begin{tabular}{|*{5}{>{\\centering\\arraybackslash}m{3.1cm}|}}\\hline\n"
            "\\rule[-0.15cm]{0pt}{0.6cm}\\textbf{А} & \\textbf{Б} & \\textbf{В} & \\textbf{Г} & \\textbf{Д} \\\\ \\hline\n"
            + клітинки + " \\\\ \\hline\n\\end{tabular}\\endgroup")


def таблиця(t, показ):
    вид = t.get("таблиця", "")
    if вид == "рисунки":
        return "\\par\\nopagebreak\\vspace{0.15cm}\\noindent" + рисунки_АД(показ) + "\\par\\vspace{0.25cm}"
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


def в_проміжку(u, w):
    """u належить проміжку w (Interval); значення на кінці перевіряється точно, решта -- наближено"""
    for кінець, відкритий in ((w.start, w.left_open), (w.end, w.right_open)):
        if кінець.is_finite and рівні(u, кінець): return not відкритий
    return bool(w.start < num(u, 30) < w.end)


def пари(t):
    """завдання на відповідність: для кожного пункту 1--3 -- номери варіантів А--Д, що йому відповідають"""
    пр = t.get("правильно") or рівні
    return [[j for j, w in enumerate(t["варіанти"]) if пр(u, w)] for u in t["обч"]()]


def блок_відповідності(t):
    """макет НМТ: умова (рисунок під нею або поруч, три рисунки «Рис. 1--3» у ряд), колонки 1--3 і А--Д, сітка відповідей;
    якщо варіанти -- рисунки (праві_рисунки), вони йдуть таблицею під колонкою пунктів"""
    ліві = "\\matchHead{%s}\n" % t["заголовок_ліво"] + "\n".join(r"\matchItem{%d}{%s}" % (i + 1, s) for i, s in enumerate(t["ліві"]))
    рис = t.get("рисунок")
    if рис and t.get("розміщення") == "поруч":
        w = t.get("ширина", 0.55)
        верх = ("\\noindent\n\\begin{minipage}[c]{%.2f\\textwidth}\n\\zadnum %s\n\\end{minipage}\\hfill\n"
                "\\begin{minipage}[c]{%.2f\\textwidth}\\centering\n\\begin{nmtfit}%s\\end{nmtfit}\n\\end{minipage}\\par\n") % (w, t["умова"], 0.96 - w, рис)
    else:
        верх = "\\zadtask{%s}\n" % t["умова"]
        if рис: верх += "\\nmtnobreak\n\\nopagebreak\\nbvspace{0.3cm}\n\\begin{center}\\begin{nmtfit}%s\\end{nmtfit}\\end{center}\n" % рис
    if t.get("рисунки_ліво"):
        верх += "\\nmtnobreak\n\\nopagebreak\\nbvspace{0.2cm}\n\\noindent" + "\\hfill".join(
            "\\begin{minipage}[t]{0.32\\textwidth}\\centering Рис.~%d\\\\[2pt]\\begin{nmtfit}%s\\end{nmtfit}\\end{minipage}" % (i + 1, p)
            for i, p in enumerate(t["рисунки_ліво"])) + "\\par\n"
    if t.get("праві_рисунки"):
        низ = ("\\noindent\\begin{minipage}[t]{0.62\\textwidth}\\vspace{0pt}\\raggedright\n%s\n\\end{minipage}\\hfill\n"
               "\\begin{minipage}[t]{0.3\\textwidth}\\vspace{0pt}\\begin{flushright}\\matchingGrid\\end{flushright}\\end{minipage}\n"
               "\\par\\nopagebreak\\vspace{0.25cm}\\noindent\\matchHead{%s}\n\\nopagebreak\\noindent%s\\par\\vspace{0.2cm}") % (
                   ліві, t["заголовок_право"], рисунки_АД(t["праві_рисунки"]))
    else:
        праві = "\n".join(r"\matchItem{%s}{%s}" % (L[j], s) for j, s in enumerate(t["праві"]))
        низ = "\\noindent\n\\matchingLayout{\n%s\n}{\n\\matchHead{%s}\n%s\n}{\n\\matchingGrid\n}" % (ліві, t["заголовок_право"], праві)
    return верх + "\\nmtnobreak\n\\nopagebreak\\nbvspace{0.3cm}\n" + низ


def відповідність(t):
    """перевірка: кожному пункту відповідає рівно один варіант, усі три різні; пастки -- лише на неправильних парах"""
    assert len(t["ліві"]) == 3 and len(t.get("праві_рисунки") or t["праві"]) == len(t["варіанти"]) == 5, t["код"]
    h = пари(t)
    assert len(h) == 3 and all(len(p) == 1 for p in h), (t["код"], "варіантів для пунктів: %s" % h)
    k = [p[0] for p in h]
    assert len(set(k)) == 3, (t["код"], "два пункти мають однакову відповідь")
    for (i, j) in t["пастки"]:
        assert 1 <= i <= 3 and 0 <= j <= 4 and k[i - 1] != j, (t["код"], "пастка на правильній парі", (i, j))
    # дистрактори конкурентні: кожен зайвий варіант -- пастка якогось пункту, у кожного пункту є пастка серед варіантів
    for j in set(range(5)) - set(k):
        assert any(jj == j for _, jj in t["пастки"]), (t["код"], "зайвий варіант %s не є пасткою жодного пункту" % L[j])
    for i in (1, 2, 3):
        assert any(ii == i for ii, _ in t["пастки"]), (t["код"], "пункт %d без пастки серед варіантів" % i)
    якість_відповідності(t, k)
    пастки = "; ".join("%d~--~%s: %s" % (i, L[j], текст) for (i, j), текст in sorted(t["пастки"].items()))
    return dict(код=t["код"], група=t["група"], назва=t["назва"], частота=t["частота"], формати=t["формати"], нмт=t["нмт"],
                latex=блок_відповідності(t), відповідь="".join(L[j] for j in k),
                відповідь_показ=", ".join("%d~--~%s" % (i + 1, L[j]) for i, j in enumerate(k)), пастки=пастки)


# ---------------------------------------------------------------- якість варіантів
# Міжнародні правила складання тестів, які НМТ теж виконує: Haladyna, Downing, Rodriguez (2002) -- 31 правило
# (усі дистрактори правдоподібні й походять із типових помилок, варіанти однорідні й приблизно однакової довжини,
# жоден варіант не вирізняється); NBME Item-Writing Guide -- вади, що підказують «тестово обізнаним»: найдовший
# правильний варіант, «конвергенція» (правильний -- центр, з якого інші отримано перестановками). Це попередження,
# а не помилки: збірка не зупиняється, список друкується наприкінці.
ЗАУВАГИ = []


def видимий_текст(s):
    s = re.sub(r"\\(?:dfrac|frac|tfrac)\{([^{}]*)\}\{([^{}]*)\}", r"\1/\2", str(s))
    s = re.sub(r"\\[A-Za-z]+", "", s)
    return re.sub(r"[{}$~^_\s]", "", s)


def словесні(показ):
    return sum(bool(re.search(r"[а-яіїєґА-ЯІЇЄҐ]{3,}", видимий_текст(p))) for p in показ) >= 3


def _число(v):
    return isinstance(v, (int, float)) or (hasattr(v, "is_number") and v.is_number is True)


def перетворення(u, w):
    """w отримано з u однією «помилкою знака чи дробу»: -u, 1/u або -1/u"""
    try:
        u, w = sympify(u), sympify(w)
        return рівні(w, -u) if u == 0 else any(рівні(w, c) for c in (-u, 1 / u, -1 / u))
    except Exception:
        return False


def якість_тесту(t, h):
    зауваги = []
    пасткові = {i for ключ in t["пастки"] for i in (ключ if isinstance(ключ, tuple) else (ключ,))}
    без = [i for i in range(5) if i != h and i not in пасткові]
    if без: зауваги.append("дистрактори без описаної помилки: " + ", ".join(str(t["показ"][i]) for i in без))
    вар = t["варіанти"]
    if all(_число(v) for v in вар) and not all("=" in str(p) or "\\int" in str(p) for p in t["показ"]):
        степінь = [sum(перетворення(вар[i], вар[j]) for j in range(5) if j != i) for i in range(5)]
        if степінь[h] >= 2 and all(степінь[h] > степінь[i] for i in range(5) if i != h):
            зауваги.append("конвергенція: правильний варіант -- центр «родини», інші -- зміна знака чи обернення")
    if словесні(t["показ"]):
        довж = [len(видимий_текст(p)) for p in t["показ"]]
        if all(довж[h] > 1.3 * довж[i] for i in range(5) if i != h):
            зауваги.append("правильний варіант помітно найдовший")
    ЗАУВАГИ.extend("%s: %s" % (t["код"], z) for z in зауваги)


def якість_відповідності(t, k):
    if t.get("праві_рисунки") or not словесні(t["праві"]): return
    довж = [len(видимий_текст(p)) for p in t["праві"]]
    зайві = [j for j in range(5) if j not in k]
    if min(довж[j] for j in k) > max(довж[j] for j in зайві):
        ЗАУВАГИ.append("%s: правильні варіанти -- три найдовші" % t["код"])


def друкувати_зауваги():
    print("якість варіантів (Haladyna et al. 2002, NBME): %s" % ("зауваг немає" if not ЗАУВАГИ else "%d зауваг" % len(ЗАУВАГИ)))
    for z in ЗАУВАГИ: print("   ", z)
    ЗАУВАГИ.clear()


def зібрати_відповідності(ТИПИ, ВИХІД):
    """каталог завдань на відповідність: літери відповідей -- як у зразку (порядок варіантів задано вручну,
    як у НМТ: числа за зростанням, проміжки й точки -- зліва направо)"""
    out = [відповідність(t) for t in ТИПИ]
    json.dump(out, open(ВИХІД, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("усі %d зразків: кожному пункту -- рівно один варіант, відповіді різні, пастки -- лише на неправильних парах; "
          "обидва зайві варіанти -- пастки пунктів, у кожного пункту є пастка" % len(out))
    print("літери відповідей:", dict(sorted(collections.Counter("".join(r["відповідь"] for r in out)).items())))
    print("відповіді:", " ".join(r["відповідь"] for r in out))
    друкувати_зауваги()


# ---------------------------------------------------------------- коротка відповідь (відкрита частина)
def число_нмт(v):
    """запис числа для бланка НМТ: ціле або скінченний десятковий дріб (з комою); інакше -- None"""
    q = Rational(sympify(v))
    d = q.q
    for p in (2, 5):
        while d % p == 0: d //= p
    if d != 1: return None
    s = format(Decimal(int(q.p)) / Decimal(int(q.q)), "f")
    if "." in s: s = s.rstrip("0").rstrip(".")
    return s.replace(".", "{,}")


def показ_числа(v):
    s = число_нмт(v)
    if s is not None: return s
    q = Rational(sympify(v))
    return (r"-\tfrac{%d}{%d}" if q < 0 else r"\tfrac{%d}{%d}") % (abs(q.p), q.q)


def блок_відкритий(t):
    s = "\\zadtask{%s}\n" % t["умова"]
    if t.get("рисунок"):
        s += "\\nmtnobreak\n\\nopagebreak\\nbvspace{0.3cm}\n\\begin{center}\\begin{nmtfit}%s\\end{nmtfit}\\end{center}\n" % t["рисунок"]
    return s + "\\nmtnobreak\n\\nopagebreak\\nbvspace{0.4cm}\n\\nmtAnswerBox"


def відкрите(t):
    """відповідь -- число для бланка; кожна типова хибна відповідь обчислена й не збігається з правильною
    (правило Бартона: хибний спосіб не має давати правильну відповідь)"""
    v = sympify(t["обч"]())
    відп = число_нмт(v)
    assert відп is not None, (t["код"], "відповідь не записується цілим числом чи скінченним десятковим дробом", v)
    assert t["пастки"], (t["код"], "немає типових хибних відповідей")
    пастки, бачені = [], set()
    for f, текст in t["пастки"]:
        w = sympify(f())
        assert w.is_real and not рівні(w, v), (t["код"], "хибний спосіб дає правильну відповідь", текст)
        assert w not in бачені, (t["код"], "дві пастки з однаковою відповіддю", текст)
        бачені.add(w)
        пастки.append("$%s$ -- %s" % (показ_числа(w), текст))
    return dict(код=t["код"], група=t["група"], назва=t["назва"], частота=t["частота"], формати=t["формати"], нмт=t["нмт"],
                latex=блок_відкритий(t), відповідь=відп, пастки="; ".join(пастки))


def зібрати_відкриті(ТИПИ, ВИХІД):
    """каталог завдань з короткою відповіддю"""
    out = [відкрите(t) for t in ТИПИ]
    json.dump(out, open(ВИХІД, "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("усі %d зразків: відповідь -- ціле число чи скінченний десятковий дріб; жоден типовий хибний спосіб "
          "не дає правильної відповіді" % len(out))
    print("відповіді:", ", ".join("%s %s" % (r["код"], r["відповідь"].replace("{,}", ",")) for r in out))


def зібрати(ТИПИ, ВИХІД):
    """перевірити кожен зразок, вирівняти літери, записати JSON каталогу"""
    природні = []
    for t in ТИПИ:
        assert len(t["показ"]) == 5 and len(t["варіанти"]) == 5, t["код"]
        h = правильні(t)
        assert len(h) == 1, (t["код"], "правильних варіантів: %s" % h)
        for ключ in t["пастки"]:
            assert h[0] not in (ключ if isinstance(ключ, tuple) else (ключ,)), (t["код"], "пастка на правильному варіанті")
        формули = all("=" in str(p) or "\\int" in str(p) for p in t["показ"])   # варіанти -- формули, значення лише для перевірки
        if "правильно" not in t and not формули:          # варіанти не збігаються за значенням (правило 22: не перекриваються)
            assert not any(рівні(t["варіанти"][i], t["варіанти"][j]) for i in range(5) for j in range(i)), (t["код"], "два однакові варіанти")
        якість_тесту(t, h[0])
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
    друкувати_зауваги()
