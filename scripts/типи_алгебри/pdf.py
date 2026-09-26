# -*- coding: utf-8 -*-
"""PDF каталогу типів тестових з алгебри: python3 scripts/типи_алгебри/pdf.py ВИХІД.pdf"""
import os, sys, json, shutil, tempfile
HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, os.path.join(ROOT, "scripts", "варіант_нмт"))
import варіант as V                                    # noqa: E402
from спільне import як_у_базі, файли_тем, нфк          # noqa: E402
from аналоги import компілювати                        # noqa: E402

ВСТУП = r"""\noindent{\small На основі 549 тестових завдань НМТ 2022--2026 з алгебри (база + НМТ з osvita); рівняння й нерівності -- в окремому каталозі.
За темами: вирази -- 173, арифметика й текстові задачі -- 103, функції й графіки -- 85, похідна, первісна й прогресії -- 76, статистика -- 44,
комбінаторика й ймовірність -- 37, тригонометрія -- 31. Для кожного типу: як часто трапляється, формати питання, приклад із НМТ і новий зразок
того самого рівня. Кожен зразок перевірено: правильний рівно один варіант, решта -- наслідки названих помилок (пастки).
Літери відповідей розподілено рівномірно. Параметри сюди не входять.}\par\vspace{0.3cm}
"""
БЛОК = r"""\par\noindent\begin{minipage}{\linewidth}
%s\par\vspace{0.25cm}\noindent{\bfseries\color{mainGreen}%s.~%s}\par\nopagebreak
\noindent{\footnotesize\color{gray!85!black}Частота: %s.\quad Формат питання: %s.}\par\nopagebreak
\noindent{\footnotesize\color{gray!85!black}Як у НМТ: %s}\par\nopagebreak\vspace{0.12cm}
\renewcommand{\thezad}{%s}
%s
\nopagebreak\noindent{\footnotesize Відповідь: \textbf{%s}.\quad Пастки: %s.}\par
\end{minipage}\par
"""


def main():
    T = json.load(open(os.path.join(ROOT, "scripts", "data", "типи_алгебри_нмт.json"), encoding="utf-8"))
    title = "Алгебра НМТ: типи тестових завдань і зразки"
    out = [V.преамбула(title, "Типи тестових завдань з алгебри НМТ"), "\\begin{document}", V.тіло_теми(файли_тем()[0][1]) + "\n",
           "\\chapterTitle{%s}\n" % title, ВСТУП]
    група = None
    for t in T:
        розділ = ""
        if t["група"] != група:                          # заголовок розділу -- в одному блоці з першим завданням
            група = t["група"]; розділ = "\\sectionTitle{%s}\n" % група
        out.append(БЛОК % (розділ, t["код"], t["назва"], t["частота"], t["формати"], t["нмт"], t["код"], як_у_базі(t["latex"]).replace(r"\par\penalty-20", ""), t["відповідь"], t["пастки"]))
    out.append("\\end{document}\n")
    ok, err, pdf, over = компілювати(нфк("\n".join(out)).replace("ʼ", "'"), tempfile.mkdtemp(), "типи_алгебри")   # у шрифті немає U+02BC
    if not ok: raise SystemExit(err)
    shutil.copy(pdf, sys.argv[1] if len(sys.argv) > 1 else "Типи_тестових_з_алгебри_НМТ.pdf")
    print("готово; рядків, що вилазять за поле:", over)


if __name__ == "__main__":
    main()
