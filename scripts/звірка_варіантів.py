# -*- coding: utf-8 -*-
"""Звірка варіантів відповіді (А--Д) завдань бази з оригіналами НМТ 2023--2026 (PDF): збірник міг переставляти варіанти.

    python3 scripts/звірка_варіантів.py ВИХІД.json [--id ID ...]

Для кожного тестового завдання з \\answerTable / \\answerTableTall знаходить завдання в оригіналі (як scripts/перемалювати.py),
читає рядок варіантів під заголовком А Б В Г Д і порівнює з базою ПОЗИЦІЯ В ПОЗИЦІЮ (за цифрами, а без цифр -- за літерами).
Вердикти: збігається / різні (які позиції) / невизначено (не знайдено заголовок А--Д: варіанти списком, рисунки тощо)."""
import os, re, sys, json, collections
HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE); sys.path.insert(0, os.path.join(HERE, "варіант_нмт"))
import звірка_рисунків as З                  # noqa: E402
import спільне as SP                         # noqa: E402
import перемалювати as П                     # noqa: E402

ЛІТЕРИ = ["А", "Б", "В", "Г", "Д"]


def аргументи(блок):
    m = re.search(r"\\answerTable(?:Tall)?\s*\{", блок)
    if not m: return None
    арг, j = [], m.end() - 1
    while len(арг) < 5:
        while j < len(блок) and блок[j] in " \n\t%":
            if блок[j] == "%": j = блок.index("\n", j)
            j += 1
        if j >= len(блок) or блок[j] != "{": return None
        г, k = 0, j
        while True:
            if блок[k] == "\\": k += 2; continue
            if блок[k] == "{": г += 1
            elif блок[k] == "}":
                г -= 1
                if not г: break
            k += 1
        арг.append(блок[j + 1:k]); j = k + 1
    return арг


def канон(s):
    s = re.sub(r"(?<!\\)%[^\n]*", "", s)
    s = re.sub(r"\\begin\{tikzpicture\}.*?\\end\{tikzpicture\}", "РИС", s, flags=re.S)
    s = s.replace("\\pi", "π").replace("\\sqrt", "√").replace("^\\circ", "").replace("°", "")
    s = s.replace("\\infty", "∞").replace("\uf0a5", "∞")
    s = re.sub(r"\\(?:mathrm|textit|text|mathbf)\{([^{}]*)\}", r"\1", s)
    s = re.sub(r"\^\s*\{[^{}]*\}|\^\s*[\w]", "", s)         # степені (одиниці см², x²) в оригіналі -- дрібні слова, відкидаємо з обох боків
    s = re.sub(r"\\[A-Za-z]+", "", s)
    s = re.sub(r"[–−‒]", "-", s)
    s = s.replace("І", "I").replace("ІІ", "II")
    знаки = re.sub(r"[^0-9\-∞π√a-zа-яіїєґ]", "", s.lower())
    знаки = re.sub(r"(?<=\d)-(?=\d)", "", знаки)               # дефіс між цифрами (проміжок «2-3») -- не знак
    return "".join(sorted(знаки))


def оригінальні_варіанти(pdf, p, y0, y1):
    ws = [w for w in З.слова(pdf, p) if y0 - 2 <= w[1] < y1]
    літери = [w for w in ws if w[4] in ЛІТЕРИ]
    # заголовок: п'ять літер А..Д в одному рядку, x зростає
    for a in літери:
        ряд = sorted([w for w in літери if abs(w[1] - a[1]) < 3.5], key=lambda w: w[0])
        буки = [w[4] for w in ряд]
        if буки == ЛІТЕРИ:
            центри = [(w[0] + w[2]) / 2 for w in ряд]
            hy = max(w[3] for w in ряд)
            колонки = [[] for _ in ЛІТЕРИ]
            висоти = sorted(w[3] - w[1] for w in ws if w[1] > hy + 1)
            мед = висоти[len(висоти) // 2] if висоти else 10
            for w in ws:
                if w[1] <= hy + 1 or w[1] > hy + 36: continue
                if (w[3] - w[1]) < 0.72 * мед and re.fullmatch(r"[0-9]", w[4]): continue      # надрядковий індекс
                c = (w[0] + w[2]) / 2
                k = min(range(5), key=lambda i: abs(центри[i] - c))
                колонки[k].append(w)
            return ["".join(x[4] + " " for x in sorted(к, key=lambda t: (round(t[1] / 3), t[0]))) for к in колонки]
    return None


def main():
    куди = sys.argv[1]
    тільки = set(sys.argv[sys.argv.index("--id") + 1:]) if "--id" in sys.argv else None
    рез = []
    for t in SP.завдання_бази():
        i = t["id"]
        if тільки and i not in тільки: continue
        арг = аргументи(t["блок"])
        if арг is None: continue
        try:
            _, pdf, знайдено = П.місце_в_оригіналі(i)
        except Exception as e:
            рез.append({"id": i, "вердикт": "не знайдено", "що": str(e)[:80]}); continue
        if not знайдено or знайдено[3] < 0.45:
            рез.append({"id": i, "вердикт": "не знайдено", "що": "схожість %.2f" % (знайдено[3] if знайдено else 0)}); continue
        ор = оригінальні_варіанти(pdf, знайдено[0], знайдено[1], знайдено[2])
        if ор is None:
            рез.append({"id": i, "вердикт": "невизначено", "що": "заголовок А-Д не знайдено", "сторінка": знайдено[0]}); continue
        база = [канон(a) for a in арг]; ориг = [канон(a) for a in ор]
        різні = [ЛІТЕРИ[k] for k in range(5) if база[k] != ориг[k]]
        рез.append({"id": i, "вердикт": "збігається" if not різні else "різні", "позиції": різні, "сторінка": знайдено[0],
                    "pdf": os.path.basename(pdf), "база": [re.sub(r"\s+", " ", a)[:40] for a in арг], "оригінал": [re.sub(r"\s+", " ", a).strip()[:40] for a in ор]})
    json.dump(рез, open(куди, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    print(collections.Counter(r["вердикт"] for r in рез))


if __name__ == "__main__":
    main()
