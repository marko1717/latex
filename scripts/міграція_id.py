# -*- coding: utf-8 -*-
"""Перенесення id завдання після правки його тексту: id = sha1 тексту без TikZ і коментарів (SP.підпис), тож зміна
тексту (умова, варіанти, рік) дає новий id, а каталоги, пробна база, класифікація й перемальовані рисунки тримаються за
старий. Використання:
    python3 scripts/міграція_id.py СТАРИЙ НОВИЙ [СТАРИЙ НОВИЙ ...]      # замінює id у scripts/data/*.json і *.py поруч
    python3 scripts/міграція_id.py --знайти СТАРИЙ                       # де id трапляється
Порядок роботи: 1) запам'ятати старий id; 2) додати правку в SOURCE_FIXES будівника; 3) зібрати; 4) новий id --
завдання з новим текстом (`SP.завдання_бази()`); 5) запустити цей скрипт; 6) зібрати ще раз і перевірити каталог."""
import os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(HERE)
ПРОПУСТИТИ = {"build_log.json", "завдання_за_оригіналом.json", "рисунки_за_оригіналом.json", "id_після_розкладки.json", "id_після_розкладки_застосовано.json"}     # останній ключується СТАРИМ id (так будівник знаходить завдання, яке замінює)


def файли():
    for d in (os.path.join(HERE, "data"),):
        for f in sorted(os.listdir(d)):
            if f.endswith(".json") and f not in ПРОПУСТИТИ: yield os.path.join(d, f)
    for корінь in (os.path.join(ROOT, "пробні"), os.path.join(HERE, "пробні_нмт"), os.path.join(HERE, "варіант_нмт")):
        for p, _, fs in os.walk(корінь):
            for f in fs:
                if f.endswith(".py"): yield os.path.join(p, f)


def знайти(i):
    return [(os.path.relpath(f, ROOT), open(f, encoding="utf-8").read().count(i)) for f in файли() if i in open(f, encoding="utf-8").read()]


def замінити(пари):
    for старий, новий in пари:
        assert re.fullmatch(r"[0-9a-f]{12}", старий) and re.fullmatch(r"[0-9a-f]{12}", новий), (старий, новий)
        for f in файли():
            t = open(f, encoding="utf-8").read()
            if старий in t:
                open(f, "w", encoding="utf-8").write(t.replace(старий, новий))
                print("%s -> %s: %s (%d)" % (старий, новий, os.path.relpath(f, ROOT), t.count(старий)))


def замінити_мапу(мапа):
    """мапа {старий: новий} -- усі id за один прохід по кожному файлу (регулярний вираз із усіх старих)"""
    ключі = [k for k, v in мапа.items() if k != v]
    if not ключі: return 0
    re_всі = re.compile(r"(?<![0-9a-f])(" + "|".join(ключі) + r")(?![0-9a-f])")
    n = 0
    for f in файли():
        t = open(f, encoding="utf-8").read()
        t2 = re_всі.sub(lambda m: мапа[m.group(1)], t)
        if t2 != t:
            open(f, "w", encoding="utf-8").write(t2); n += 1
    return n


def оновити_розкладку():
    """після кожної зміни розкладки: id у даних (каталог, пробна база...) = «застосована» мапа (id_після_розкладки_застосовано.json), а будівник
    щойно записав нову (id_після_розкладки.json): переносимо різницю й запам'ятовуємо нову як застосовану"""
    import json
    нова = json.load(open(os.path.join(HERE, "data", "id_після_розкладки.json"), encoding="utf-8"))
    шлях = os.path.join(HERE, "data", "id_після_розкладки_застосовано.json")
    застосована = json.load(open(шлях, encoding="utf-8")) if os.path.exists(шлях) else {}
    різниця = {}
    for до, після in нова.items():
        було = застосована.get(до, до)
        if було != після: різниця[було] = після
    for до, було in застосована.items():                    # блок повернувся до початкового вигляду
        if до not in нова and було != до: різниця[було] = до
    n = замінити_мапу(різниця)
    json.dump(нова, open(шлях, "w", encoding="utf-8"), ensure_ascii=False, indent=0)
    return n, len(різниця)


def прибрати(i):
    """завдання вилучено з бази: прибирає його записи (елементи списків з "id" == i і ключі-id) з data/*.json"""
    import json
    for f in файли():
        if not f.endswith(".json") or os.path.basename(f) in ПРОПУСТИТИ: continue
        t = open(f, encoding="utf-8").read()
        if i not in t: continue
        d = json.loads(t)
        def обх(o):
            if isinstance(o, list): return [обх(x) for x in o if not (isinstance(x, dict) and x.get("id") == i)]
            if isinstance(o, dict): return {k: обх(v) for k, v in o.items() if k != i}
            return o
        н = обх(d)
        компактний = t.startswith("[\n{") and t.count("\n") > 50 and "\n  " not in t[:200]       # формат «по рядку на запис» (SP.зберегти_json)
        if компактний:
            with open(f, "w", encoding="utf-8") as g:
                g.write("[\n" + ",\n".join(json.dumps(r, ensure_ascii=False, separators=(",", ":")) for r in н) + "\n]\n")
        else:
            open(f, "w", encoding="utf-8").write(json.dumps(н, ensure_ascii=False, indent=1) + ("\n" if t.endswith("\n") else ""))
        print("прибрано %s: %s" % (i, os.path.relpath(f, ROOT)))


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--оновити":
        print("змінено файлів: %d, id: %d" % оновити_розкладку())
    elif a and a[0] == "--мапа":
        import json
        м = json.load(open(a[1], encoding="utf-8"))
        print("змінено файлів:", замінити_мапу(м), "з id:", len(м))
    elif a and a[0] == "--прибрати":
        for i in a[1:]: прибрати(i)
    elif a and a[0] == "--знайти":
        for f, n in знайти(a[1]): print(n, f)
    else:
        assert len(a) % 2 == 0 and a, __doc__
        замінити(list(zip(a[::2], a[1::2])))
