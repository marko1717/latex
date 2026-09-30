# -*- coding: utf-8 -*-
"""Перевірка ОДНОГО завдання-кандидата для пробного НМТ -- до того, як вписати його в пробні/<пробний>/спец.py.

    python3 scripts/пробні_нмт/кандидат.py CANDIDATE.py [--mock клас_1] [--out ТЕКА_ДЛЯ_PNG]

CANDIDATE.py -- фрагмент у форматі пробні/клас_1/спец.py: допоміжні змінні + рівно один виклик з(...).
Виконується в просторі імен спец.py (усі імпорти: R, sqrt, log, solve, Interval, Рис, осі, плавна, поруч, призма,
піраміда, правильний, xf, D, парна, ... і СХЕМА_І_ФОТО). Кандидат ЗАМІНЮЄ завдання свого слота в поточному пробному.

Друкує: перевірки збирача (рівно один правильний варіант, пастки, якість дистракторів / відповідь для бланка),
перевірку складу (родини тем, заборонені теми й типи, обов'язкові умови) і шлях до PNG сторінки з завданням."""
import os, sys, io, json, re, tempfile, subprocess, contextlib, importlib.util, traceback, hashlib
ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "scripts", "пробні_нмт"))
import пробний as П                                           # noqa: E402
from спільне import СТРУКТУРА_2026, РОДИНИ, МОЖНА_ПОВТОРЮВАТИ   # noqa: E402
from аналоги import компілювати                               # noqa: E402

cand = os.path.abspath(sys.argv[1])
mock = sys.argv[sys.argv.index("--mock") + 1] if "--mock" in sys.argv else "клас_1"
RENDERS = sys.argv[sys.argv.index("--out") + 1] if "--out" in sys.argv else tempfile.mkdtemp(prefix="кандидат_")
os.makedirs(RENDERS, exist_ok=True)

spec = importlib.util.spec_from_file_location("спец_кандидата", os.path.join(ROOT, "пробні", mock, "спец.py"))
m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
КОНФІГ, ПОТОЧНІ = m.КОНФІГ, list(m.ЗАВДАННЯ)
m.ЗАВДАННЯ = []
код = open(cand, encoding="utf-8").read()
exec(compile(код, cand, "exec"), m.__dict__)
assert len(m.ЗАВДАННЯ) == 1, "у кандидаті має бути рівно один виклик з(...), а є %d" % len(m.ЗАВДАННЯ)
c = m.ЗАВДАННЯ[0]
k = СТРУКТУРА_2026.index(c["слот"])
print("слот %d (%s), тип %s, теми %s, родини %s" % (k + 1, c["слот"], c["тип_каталогу"], c["теми"],
      sorted(set(c["родини"]) if c.get("родини") else {РОДИНИ.get(u, "?") for u in c["теми"]})))

# ---- склад: кандидат замість поточного завдання цього слота
нові = list(ПОТОЧНІ); нові[k] = c
T = П.типи_каталогів()
try:
    П.перевірити_склад(КОНФІГ, нові, T)
    print("СКЛАД: ок (з рештою поточних завдань пробного)")
except AssertionError as e:
    print("СКЛАД: ЗАУВАГА --", e)
    rod = lambda z: (set(z["родини"]) if z.get("родини") else {РОДИНИ.get(u, "?") for u in z["теми"]}) - МОЖНА_ПОВТОРЮВАТИ
    for i, z in enumerate(нові, 1):
        if i != k + 1 and rod(z) & rod(c): print("   спільна родина з поточним № %d (%s): %s" % (i, z["тип_каталогу"], rod(z) & rod(c)))
print("назва типу:", T[c["тип_каталогу"]]["назва"])

# ---- перевірки збирача
tmp = tempfile.mkdtemp()
z = П.заповнити(c, k + 1)
buf = io.StringIO()
try:
    with contextlib.redirect_stdout(buf):
        if k < 15: П.З.зібрати([z], os.path.join(tmp, "r.json"))
        elif k < 18: П.З.зібрати_відповідності([z], os.path.join(tmp, "r.json"))
        else: П.З.зібрати_відкриті([z], os.path.join(tmp, "r.json"))
except BaseException:
    print(buf.getvalue()); traceback.print_exc(); print("ЗБИРАЧ: ПОМИЛКА"); sys.exit(1)
print(buf.getvalue().strip())
r = json.load(open(os.path.join(tmp, "r.json"), encoding="utf-8"))[0]
print("ВІДПОВІДЬ:", r["відповідь"])
print("ПАСТКИ:", r["пастки"])
print("РОЗВʼЯЗОК:", c.get("розвʼязок", ""))

# ---- сторінка з завданням
out = [dict(номер=k + 1, latex=r["latex"])]
tex = П.документ(dict(КОНФІГ, вступ="Перевірка кандидата."), out).replace("\\setcounter{zad}{0}", "\\setcounter{zad}{%d}" % k)
work = tempfile.mkdtemp()
ім = "канд_" + hashlib.md5(cand.encode()).hexdigest()[:8]
ok, err, pdf, over = компілювати(tex, work, ім)
ok, err, pdf, over = компілювати(tex, work, ім)
if not ok: print("LATEX: ПОМИЛКА\n" + err); sys.exit(1)
png = os.path.join(RENDERS, os.path.splitext(os.path.basename(cand))[0])
subprocess.run(["pdftoppm", "-r", "110", "-png", "-f", "1", "-l", "1", pdf, png], check=True)
print("LATEX: ок, рядків за полем:", over)
print("PNG:", [os.path.join(RENDERS, f) for f in sorted(os.listdir(RENDERS)) if f.startswith(os.path.basename(png))])
