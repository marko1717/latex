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
ПРОПУСТИТИ = {"build_log.json", "завдання_за_оригіналом.json"}     # останній ключується СТАРИМ id (так будівник знаходить завдання, яке замінює)


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


if __name__ == "__main__":
    a = sys.argv[1:]
    if a and a[0] == "--знайти":
        for f, n in знайти(a[1]): print(n, f)
    else:
        assert len(a) % 2 == 0 and a, __doc__
        замінити(list(zip(a[::2], a[1::2])))
