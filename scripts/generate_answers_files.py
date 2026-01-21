#!/usr/bin/env python3
"""
Скрипт для створення файлів відповідей на основі JSON.
"""

import json
import os

def generate_tex_answers(topic_name, answers):
    """Генерує LaTeX код для відповідей"""
    tex = r"""\documentclass[12pt]{extarticle}
\usepackage{fontspec}
\usepackage{polyglossia}
\setdefaultlanguage{ukrainian}

\defaultfontfeatures{Ligatures=TeX}
\setmainfont{Liberation Serif}

\usepackage[a4paper,margin=2cm]{geometry}
\usepackage{multicol}
\usepackage{xcolor}

\definecolor{headerblue}{RGB}{0, 102, 204}

\begin{document}

\begin{center}
{\Large\textbf{\color{headerblue}ВІДПОВІДІ}}
\end{center}

\begin{center}
{\large """ + f"Тема: {topic_name}" + r"""}
\end{center}

\vspace{0.5cm}

\begin{multicols}{5}
\noindent
"""

    for i, ans in enumerate(answers, 1):
        tex += f"{i}. {ans}"
        if i < len(answers):
            tex += " \\\\\n"
        else:
            tex += "\n"

    tex += r"""\end{multicols}

\end{document}
"""
    return tex

def main():
    base_dir = "/Users/markiyankharchuk/Desktop/НМТ_по_темах_латех"
    json_path = os.path.join(base_dir, 'answers_all.json')

    with open(json_path, 'r', encoding='utf-8') as f:
        data = json.load(f)

    # Список директорій
    dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

    for topic_name, files in data.items():
        # Збираємо всі відповіді
        all_answers = []
        for file_name, file_answers in files.items():
            all_answers.extend(file_answers)

        if not all_answers:
            continue

        # Шукаємо директорію
        topic_dir = None
        for d in dirs:
            if d == topic_name or d.startswith(topic_name.split('.')[0] + '.'):
                full_path = os.path.join(base_dir, d)
                if os.path.isdir(full_path) and d != 'generated':
                    topic_dir = full_path
                    break

        if topic_dir:
            # Перевіряємо, чи вже є файл
            tex_path = os.path.join(topic_dir, 'відповіді.tex')
            if not os.path.exists(tex_path):
                tex_content = generate_tex_answers(topic_name, all_answers)
                try:
                    with open(tex_path, 'w', encoding='utf-8') as f:
                        f.write(tex_content)
                    print(f"✅ Створено: {tex_path}")
                except Exception as e:
                    print(f"❌ Помилка: {e}")
            else:
                print(f"ℹ️  Вже існує: {tex_path}")

if __name__ == "__main__":
    main()
