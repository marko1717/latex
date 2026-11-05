# -*- coding: utf-8 -*-
"""PDF каталогу типів: python3 scripts/типи_рівнянь/pdf.py ВИХІД.pdf"""
import os, sys, json, shutil, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts", "варіант_нмт"))
import варіант as V                                    # noqa: E402
from спільне import як_у_базі, файли_тем, нфк          # noqa: E402
from аналоги import компілювати                        # noqa: E402

ВСТУП = r"""\noindent{\small На основі 318 завдань НМТ 2022--2026 (база + НМТ з osvita): 177 рівнянь, 55 систем рівнянь, 68 нерівностей, 18 систем нерівностей -- і правил користувача:
праворуч у кореневому рівнянні лише число, а питання -- про проміжок (щоб не вгадували підстановкою), або під коренем $-2x$;
показникові -- зведення до однієї основи (можна десяткова) чи винесення за дужки; логарифмічні -- за означенням із простою дією або основою, меншою за 1;
у нерівностях праворуч нуль (лінійні, квадратні, метод інтервалів) або «яке число є розв'язком»; у системах рівнянь цікавіше, коли одне рівняння лише з $x$;
системи нерівностей можна трохи складніше. Кожен зразок перевірено: правильний рівно один варіант, решта -- наслідки названих помилок.
Параметр (коротка відповідь) сюди не входить.}\par\vspace{0.3cm}
"""
БЛОК = r"""\par\noindent\begin{minipage}{\linewidth}
\par\vspace{0.25cm}\noindent{\bfseries\color{mainGreen}%s.~%s}\par\nopagebreak
\noindent{\footnotesize\color{gray!85!black}Частота: %s.\quad Формат питання: %s.}\par\nopagebreak
\noindent{\footnotesize\color{gray!85!black}Як у НМТ: %s}\par\nopagebreak\vspace{0.12cm}
\renewcommand{\thezad}{%s}
%s
\nopagebreak\noindent{\footnotesize Відповідь: \textbf{%s}.\quad Пастки: %s.}\par
\end{minipage}\par
"""


def main():
    T = json.load(open(os.path.join(ROOT, "scripts", "data", "типи_рівнянь_нмт.json"), encoding="utf-8"))
    title = "Рівняння, системи й нерівності НМТ: типи і зразки"
    out = [V.преамбула(title, "Типи рівнянь і нерівностей НМТ"), "\\begin{document}", V.тіло_теми(файли_тем()[0][1]) + "\n",
           "\\chapterTitle{%s}\n" % title, ВСТУП]
    група = None
    for t in T:
        if t["група"] != група:
            група = t["група"]; out.append("\\sectionTitle{%s}\n" % група)
        out.append(БЛОК % (t["код"], t["назва"], t["частота"], t["формати"], t["нмт"], t["код"], як_у_базі(t["latex"]).replace(r"\par\penalty-20", ""), t["відповідь"], t["пастки"]))
    out.append("\\end{document}\n")
    ok, err, pdf, over = компілювати(нфк("\n".join(out)).replace("ʼ", "'"), tempfile.mkdtemp(), "типи")   # у шрифті немає U+02BC
    if not ok: raise SystemExit(err)
    shutil.copy(pdf, sys.argv[1] if len(sys.argv) > 1 else "Типи_рівнянь_і_нерівностей_НМТ.pdf")
    print("готово; рядків, що вилазять за поле:", over)


if __name__ == "__main__":
    main()
