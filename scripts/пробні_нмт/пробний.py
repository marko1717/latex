# -*- coding: utf-8 -*-
"""Пробний НМТ з математики: 22 авторські завдання за структурою НМТ 2026, кожне -- нове завдання певного типу з
каталогів типів (scripts/типи_*), перевірене тими самими засобами, що й зразки каталогів (scripts/типи_спільне/збирач.py):
рівно один правильний варіант, дистрактори -- названі типові помилки, вирівняні літери відповідей, різні ключі 16--18,
відповідь для бланка -- ціле число чи скінченний десятковий дріб, кожна пастка обчислена хибним способом.

    python3 scripts/пробні_нмт/пробний.py пробні/клас_1

У теці пробного: спец.py (КОНФІГ і ЗАВДАННЯ у порядку слотів), після збирання -- завдання.json, склад.json
(використані завдання -- для бази, щоб наступні пробні їх не повторювали), <Файл>.tex, <Файл>_без_водяного_знака.tex
і <Файл>_відповіді.tex (ключ, розв'язки, типи й пастки -- для вчителя; для каналу -- окремим файлом після пробного).

Перевірки складу: 22 слоти в порядку СТРУКТУРА_2026; тип кожного завдання належить слоту; кожна родина тем (прогресія,
логарифми, призма, піраміда ...) -- щонайбільше раз, крім функцій; заборонені теми й типи з КОНФІГ не трапляються."""
import os, sys, json, importlib.util, collections, tempfile, shutil, re
HERE = os.path.dirname(os.path.abspath(__file__))
SCRIPTS = os.path.dirname(HERE)
ROOT = os.path.dirname(SCRIPTS)
sys.path.insert(0, os.path.join(SCRIPTS, "варіант_нмт"))
sys.path.insert(0, os.path.join(SCRIPTS, "типи_спільне"))
sys.path.insert(0, HERE)
import збирач as З                                     # noqa: E402
import варіант as V                                     # noqa: E402
from спільне import СТРУКТУРА_2026, РОДИНИ, МОЖНА_ПОВТОРЮВАТИ, як_у_базі, файли_тем, нфк   # noqa: E402
from аналоги import компілювати                         # noqa: E402
from база import СЛОТИ, КАТАЛОГИ, ТИП_ЗАВДАННЯ         # noqa: E402

L = "АБВГД"


def завантажити_спец(тека):
    spec = importlib.util.spec_from_file_location("спец_пробного", os.path.join(тека, "спец.py"))
    m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
    return m.КОНФІГ, m.ЗАВДАННЯ


def типи_каталогів():
    T = {}
    for кат, f in КАТАЛОГИ.items():
        for t in json.load(open(os.path.join(SCRIPTS, "data", f + "_нмт.json"), encoding="utf-8")):
            T["%s:%s" % (кат, t["код"])] = t
    return T


def перевірити_склад(КОНФІГ, ЗАВДАННЯ, T):
    assert len(ЗАВДАННЯ) == 22, "у пробному має бути 22 завдання, а не %d" % len(ЗАВДАННЯ)
    родини = collections.Counter()
    for i, (z, слот) in enumerate(zip(ЗАВДАННЯ, СТРУКТУРА_2026), 1):
        assert z["слот"] == слот, (i, z["слот"], слот)
        assert z["тип_каталогу"] in T, (i, "невідомий тип", z["тип_каталогу"])
        кат, код = z["тип_каталогу"].split(":")
        assert any(кат == c and T[z["тип_каталогу"]]["група"].startswith(g) for c, g in СЛОТИ[слот]), (i, z["тип_каталогу"], "не з цього слота")
        заб = set(z["теми"]) & set(КОНФІГ.get("заборонені_теми", []))
        assert not заб, (i, "заборонені теми", заб)
        assert z["тип_каталогу"] not in КОНФІГ.get("заборонені_типи", []), (i, "заборонений тип", z["тип_каталогу"])
        for р in (set(z["родини"]) if z.get("родини") else {РОДИНИ[u] for u in z["теми"]}) - МОЖНА_ПОВТОРЮВАТИ: родини[р] += 1
    повтори = {р: n for р, n in родини.items() if n > 1}
    assert not повтори, ("родини тем повторюються", повтори)
    for ключ, (слот, умова) in КОНФІГ.get("обовʼязково", {}).items():
        z = ЗАВДАННЯ[СТРУКТУРА_2026.index(слот)]
        assert умова(z), ("не виконано обов'язкову умову", ключ)


def заповнити(z, i):
    """поля, яких чекає збирач каталогів (код, група тощо)"""
    return dict(z, код=str(i), група=z["слот"], назва=z["тип_каталогу"], частота="", формати="", нмт="")


def вирівняти(тести, готові):
    """літери 1--15: рівно по 3 на кожну, без трьох однакових поспіль; закріплені (фіксований) не рухаються;
    де можна -- природна літера (найменше перестановок). Перевірки й зауваги якості вже зробив З.зібрати."""
    природні = [З.правильні(t)[0] for t in тести]
    фікс = {i for i, t in enumerate(тести) if t.get("фіксований")}
    лічба = collections.Counter(природні[i] for i in фікс)
    ціль = [None] * 15
    for i in фікс: ціль[i] = природні[i]
    for i in range(15):
        if i in фікс: continue
        def штраф(g):
            поспіль = i >= 2 and ціль[i - 1] == g and ціль[i - 2] == g
            наступні = i + 1 < 15 and ціль[i + 1] == g and (i + 2 < 15 and ціль[i + 2] == g or i >= 1 and ціль[i - 1] == g)
            return (лічба[g] >= 3, поспіль or наступні, g != природні[i], лічба[g])
        g = min(range(5), key=штраф)
        ціль[i] = g; лічба[g] += 1
    out = []
    for t, r, k, g in zip(тести, готові, природні, ціль):
        σ = list(range(5)); σ[k], σ[g] = g, k
        order = sorted(range(5), key=lambda i: σ[i])
        t2 = dict(t, показ=[t["показ"][i] for i in order], варіанти=[t["варіанти"][i] for i in order])
        assert З.правильні(t2) == [g], (t["код"], g)
        out.append(dict(r, latex=З.блок(t2, t2["показ"]), відповідь=L[g], пастки=З.пастки_текст(t["пастки"], σ)))
    return out


def зібрати(тека):
    КОНФІГ, ЗАВДАННЯ = завантажити_спец(тека)
    T = типи_каталогів()
    перевірити_склад(КОНФІГ, ЗАВДАННЯ, T)
    tmp = tempfile.mkdtemp()
    тести = [заповнити(z, i) for i, z in enumerate(ЗАВДАННЯ[:15], 1)]
    відп = [заповнити(z, i) for i, z in enumerate(ЗАВДАННЯ[15:18], 16)]
    відкр = [заповнити(z, i) for i, z in enumerate(ЗАВДАННЯ[18:], 19)]
    З.зібрати(тести, os.path.join(tmp, "т.json"))
    З.зібрати_відповідності(відп, os.path.join(tmp, "в.json"))
    З.зібрати_відкриті(відкр, os.path.join(tmp, "к.json"))
    готові = sum((json.load(open(os.path.join(tmp, f), encoding="utf-8")) for f in ("т.json", "в.json", "к.json")), [])
    готові[:15] = вирівняти(тести, готові[:15])
    ключі = [r["відповідь"] for r in готові[15:18]]
    assert len(set(ключі)) == 3, ("ключі 16--18 однакові", ключі)
    out = []
    for i, (z, r) in enumerate(zip(ЗАВДАННЯ, готові), 1):
        out.append(dict(id="%s-%02d" % (КОНФІГ["id"], i), номер=i, слот=z["слот"], тип_каталогу=z["тип_каталогу"],
                        назва_типу=z.get("назва_у_ключі") or T[z["тип_каталогу"]]["назва"], теми=z["теми"], тип=ТИП_ЗАВДАННЯ[z["слот"]],
                        latex=r["latex"], відповідь=r["відповідь"], пастки=r["пастки"], розвʼязок=z.get("розвʼязок", ""),
                        рисунок=bool(z.get("рисунок"))))
    json.dump(out, open(os.path.join(тека, "завдання.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    json.dump(dict(назва=КОНФІГ["назва"], для=КОНФІГ.get("для", ""), завдання=[z["id"] for z in out]),
              open(os.path.join(тека, "склад.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("літери тестів:", "".join(z["відповідь"] for z in out[:15]), dict(collections.Counter(z["відповідь"] for z in out[:15])))
    print("ключі відповідностей:", ключі, "| короткі відповіді:", [z["відповідь"] for z in out[18:]])
    return КОНФІГ, out


# ---------------------------------------------------------------- LaTeX
def документ(КОНФІГ, out):
    title = КОНФІГ["назва"]
    s = [V.преамбула(title, КОНФІГ.get("колонтитул", title)), "\\begin{document}",
         "\\relpenalty=10000 \\binoppenalty=10000   % формула в рядку не розривається після «=» чи «+»",
         "% макроси бази\n" + V.тіло_теми(файли_тем()[0][1]) + "\n\\setcounter{zad}{0}\n", "\\chapterTitle{%s}\n" % title,
         "\\noindent{\\small %s}\\par\\vspace{0.4cm}\n" % КОНФІГ["вступ"]]
    for z in out:
        if z["номер"] in V.ІНСТРУКЦІЇ: s.append("\\instructionBox{%s}\n" % V.ІНСТРУКЦІЇ[z["номер"]])
        блок = re.sub(r"(\\begin\{minipage\}\[c\]\{[0-9.]+\\textwidth\}\n)(\\zadnum)", r"\1\\raggedright\2", z["latex"])   # текст біля рисунка -- без розтягнутих пробілів
        s.append("\\begin{samepage}\n%s\n\\end{samepage}\n" % як_у_базі(V.чистий_блок(блок, False)))
    s.append("\\end{document}\n")
    return нфк("\n".join(s))


def відповіді(КОНФІГ, out):
    title = КОНФІГ["назва"] + ": відповіді"
    s = [V.преамбула(title, КОНФІГ.get("колонтитул", КОНФІГ["назва"])), "\\begin{document}", "\\chapterTitle{%s}\n" % title]
    rows = ["%d & %s \\\\ \\hline" % (z["номер"], V.відповідь_латех(z["відповідь"], z["тип"])) for z in out]
    s.append("\\begin{center}\\renewcommand{\\arraystretch}{1.25}\n\\begin{tabular}{|c|c||c|c||c|c|}\\hline\n"
             "\\textbf{№} & \\textbf{Відповідь} & \\textbf{№} & \\textbf{Відповідь} & \\textbf{№} & \\textbf{Відповідь} \\\\ \\hline\n")
    трійки = [out[i:i + 8] for i in range(0, 22, 8)]
    for k in range(8):
        клітинки = []
        for g in трійки:
            if k < len(g): клітинки += [str(g[k]["номер"]), V.відповідь_латех(g[k]["відповідь"], g[k]["тип"])]
            else: клітинки += ["", ""]
        s.append(" & ".join(клітинки) + " \\\\ \\hline")
    s.append("\\end{tabular}\\end{center}\n")
    s.append("\\noindent{\\small\\color{gray!80!black}Оцінювання: 1--15 -- по 1 балу; 16--18 -- по 1 балу за кожну правильно встановлену "
             "відповідність (до 3 балів); 19--22 -- по 2 бали. Разом 32 бали.}\\par\\vspace{0.3cm}\n")
    if КОНФІГ.get("розвʼязки", True):
        s.append("\\sectionTitle{Розв'язки й типові помилки}\n")
        for z in out:
            s.append("\\par\\noindent\\textbf{%d.} %s\\quad{\\small\\color{gray!80!black}(%s)}\\par\\nopagebreak\n" % (
                z["номер"], (z["розвʼязок"] or "").replace("ʼ", "'"), z["назва_типу"].replace("ʼ", "'")))
            if z["пастки"]:
                s.append("\\noindent{\\footnotesize\\color{gray!85!black}Типові помилки: %s.}\\par\\vspace{0.15cm}\n" % z["пастки"].replace("ʼ", "'"))
    s.append("\\end{document}\n")
    return нфк("\n".join(s))


def записати_pdf(тека, КОНФІГ, out, куди=None):
    """.tex -- у теці «пробні» (один рівень від кореня, як «варіанти»: шляхи до шрифтів і рисунків тем ті самі, Overleaf збирає)"""
    name = КОНФІГ["файл"]
    тека = os.path.dirname(тека)
    tex = {name: документ(КОНФІГ, out), name + "_відповіді": відповіді(КОНФІГ, out)}
    for n, t in tex.items():
        open(os.path.join(тека, n + ".tex"), "w", encoding="utf-8").write(t)
    open(os.path.join(тека, name + "_без_водяного_знака.tex"), "w", encoding="utf-8").write(нфк(
        "%% %s без водяного знака @pvtr2525 -- версія для вчителів.\n\\def\\nmtnowatermark{}\n\\input{%s}\n" % (КОНФІГ["назва"], name)))
    pdfs = []
    for n, t in list(tex.items()) + [(name + "_без_водяного_знака", "\\def\\nmtnowatermark{}\n" + tex[name])]:
        work = tempfile.mkdtemp()
        ok, err, pdf, over = компілювати(t, work, "пробний")
        ok2, err2, pdf, over = компілювати(t, work, "пробний")          # другий прохід -- посилання й nmtfit
        if not ok2: raise SystemExit("%s: помилка LaTeX\n%s" % (n, err2))
        dst = os.path.join(куди or тека, n + ".pdf")
        shutil.copy(pdf, dst); pdfs.append(dst)
        print("готово:", dst, "| рядків за полем:", over)
    return pdfs


if __name__ == "__main__":
    тека = os.path.abspath(sys.argv[1])
    КОНФІГ, out = зібрати(тека)
    записати_pdf(тека, КОНФІГ, out, sys.argv[2] if len(sys.argv) > 2 else None)
