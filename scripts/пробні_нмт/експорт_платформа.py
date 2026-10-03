# -*- coding: utf-8 -*-
"""Експорт пробного НМТ для платформи LearningPlatform (nmt-platform): .tex у форматі, який розуміє її парсер
scripts/parse_variant.py (22 завдання за \\zadtask/\\zadnum, варіанти в \\answerTable, пункти відповідностей як
\\textbf{1..3}/\\textbf{А..Д}, ключ у кінці файлу після \\sectionTitle{ВІДПОВІДІ}), плюс JSON з відповідями,
розв'язками й типовими помилками, рисунки-фото поруч і PDF.

    python3 scripts/пробні_нмт/експорт_платформа.py пробні/канал_1 [ТЕКА]

ТЕКА за замовчуванням -- ~/Downloads/Пробні_НМТ/<Файл>_для_платформи. Перевірка парсером платформи:
    python3 <nmt-platform>/scripts/parse_variant.py ТЕКА/<Файл>.tex   (22/22, ключ 22)
"""
import os, re, sys, json, shutil, importlib.util, unicodedata
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
L = "АБВГД"


def нфк(s): return unicodedata.normalize("NFC", s)


def пункти_як_textbf(tex):
    """\\matchItem{1}{текст} -> \\textbf{1}\\quad текст\\\\[2pt] (парсер платформи шукає пункти й варіанти за \\textbf)"""
    out, i = [], 0
    while True:
        k = tex.find("\\matchItem{", i)
        if k < 0: out.append(tex[i:]); return "".join(out)
        out.append(tex[i:k])
        j = tex.index("}", k + len("\\matchItem{"))
        мітка = tex[k + len("\\matchItem{"):j]
        assert tex[j + 1] == "{", "очікувався текст пункту"
        d, p = 0, j + 1
        while True:
            c = tex[p]
            if c == "\\": p += 2; continue
            if c == "{": d += 1
            elif c == "}":
                d -= 1
                if d == 0: break
            p += 1
        текст = tex[j + 2:p].strip()
        out.append("\\textbf{%s}\\quad %s\\\\[2pt]" % (мітка, текст))
        i = p + 1


def рядок_ключа(z):
    n, a, тип = z["номер"], z["відповідь"], z["тип"]
    if тип == "matching": return "\\textbf{%d.}\\ %s" % (n, ", ".join("%d--%s" % (i + 1, x) for i, x in enumerate(a)))
    if тип == "input": return "\\textbf{%d.}\\ $%s$" % (n, str(a).replace(",", "{,}").replace(".", "{,}"))
    return "\\textbf{%d.}\\ %s" % (n, a)


def main(тека, куди=None):
    тека = os.path.abspath(тека)
    spec = importlib.util.spec_from_file_location("спец_експорту", os.path.join(тека, "спец.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    К = m.КОНФІГ
    завдання = json.load(open(os.path.join(тека, "завдання.json"), encoding="utf-8"))
    assert len(завдання) == 22
    файл = К["файл"]
    куди = os.path.abspath(куди or os.path.expanduser("~/Downloads/Пробні_НМТ/%s_для_платформи" % файл))
    os.makedirs(куди, exist_ok=True)
    tex = open(os.path.join(ROOT, "пробні", файл + ".tex"), encoding="utf-8").read()
    # рисунки-фото: копія поруч, шлях -- просто ім'я файла
    фото = []
    def фото_поруч(mm):
        шлях = os.path.normpath(os.path.join(ROOT, "пробні", mm.group(2)))
        ім = os.path.basename(шлях); shutil.copy(шлях, os.path.join(куди, ім)); фото.append(ім)
        return mm.group(1) + "{" + ім + "}"
    tex = re.sub(r"(\\includegraphics(?:\[[^\]]*\])?)\{([^}]*)\}", фото_поруч, tex)
    tex = пункти_як_textbf(tex)
    ключ = "\n".join(рядок_ключа(z) + "\\par" for z in завдання)
    tex = tex.replace("\\end{document}", "\\clearpage\n\\sectionTitle{ВІДПОВІДІ}\n" + ключ + "\n\\end{document}")
    open(os.path.join(куди, файл + ".tex"), "w", encoding="utf-8").write(нфк(tex))
    # JSON: усе, що потрібно для блоків завдань на сайті
    записи = []
    for z in завдання:
        a = z["відповідь"]
        записи.append(dict(номер=z["номер"], тип={"single": "single", "matching": "matching", "input": "input"}[z["тип"]],
                           відповідь=({str(i + 1): x for i, x in enumerate(a)} if z["тип"] == "matching" else a),
                           розвʼязок=z["розвʼязок"], типові_помилки=z["пастки"], тип_завдання=z["назва_типу"], слот=z["слот"],
                           рисунок=z["рисунок"], latex=z["latex"]))
    json.dump(dict(назва=К["назва"], для=К.get("для", ""), структура="15 single (1 бал) + 3 matching (до 3 балів) + 4 input (2 бали) = 32 бали",
                   фото=фото, завдання=записи),
              open(os.path.join(куди, файл + ".json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    for суф in ("", "_відповіді", "_без_водяного_знака"):
        p = os.path.join(ROOT, "пробні", файл + суф + ".pdf")
        if os.path.exists(p): shutil.copy(p, куди)
    print("записано в", куди)
    for f in sorted(os.listdir(куди)): print("  ", f)


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2] if len(sys.argv) > 2 else None)
