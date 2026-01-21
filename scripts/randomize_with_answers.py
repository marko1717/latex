#!/usr/bin/env python3
"""
Скрипт для рандомізації відповідей у файлах завдань НМТ
з генерацією файлів правильних відповідей.

Логіка: перший аргумент answerTable завжди є правильною відповіддю.
Після перемішування визначаємо нову позицію правильної відповіді.
"""

import re
import random
import os
import sys
import json
from pathlib import Path

def extract_braced_args(text, start_pos, num_args=5):
    """
    Витягує num_args аргументів у фігурних дужках, починаючи з позиції start_pos.
    Правильно обробляє вкладені дужки.
    Повертає (список_аргументів, кінцева_позиція) або (None, start_pos) якщо не вдалося.
    """
    args = []
    pos = start_pos

    for _ in range(num_args):
        # Пропускаємо пробіли та переноси рядків
        while pos < len(text) and text[pos] in ' \t\n':
            pos += 1

        if pos >= len(text) or text[pos] != '{':
            return None, start_pos

        # Знаходимо закриваючу дужку з урахуванням вкладеності
        depth = 0
        arg_start = pos + 1
        while pos < len(text):
            if text[pos] == '{':
                depth += 1
            elif text[pos] == '}':
                depth -= 1
                if depth == 0:
                    args.append(text[arg_start:pos])
                    pos += 1
                    break
            pos += 1
        else:
            return None, start_pos

    return args, pos

def shuffle_answers_and_track(content):
    """
    Знаходить всі виклики answerTable* та перемішує відповіді.
    Повертає (новий_контент, список_відповідей)
    де список_відповідей = [('А'|'Б'|'В'|'Г'|'Д'), ...]
    """
    # Патерни команд (в порядку від довших до коротших)
    commands = ['\\answerTableBig', '\\answerTableTall', '\\answerTableSmall', '\\answerTable']
    labels = ['А', 'Б', 'В', 'Г', 'Д']

    answers = []
    result = content
    task_num = 0

    for cmd in commands:
        new_result = ""
        i = 0
        while i < len(result):
            # Шукаємо команду
            idx = result.find(cmd, i)
            if idx == -1:
                new_result += result[i:]
                break

            # Перевіряємо, що це саме ця команда, а не частина іншої
            is_exact = True
            if cmd == '\\answerTable':
                suffix_start = idx + len(cmd)
                if suffix_start < len(result):
                    next_char = result[suffix_start]
                    if next_char.isalpha():
                        is_exact = False

            if not is_exact:
                new_result += result[i:idx + len(cmd)]
                i = idx + len(cmd)
                continue

            # Додаємо все до команди
            new_result += result[i:idx]

            # Витягуємо 5 аргументів
            args, end_pos = extract_braced_args(result, idx + len(cmd), 5)

            if args is None or len(args) != 5:
                # Не вдалося розпарсити, залишаємо як є
                new_result += result[idx:idx + len(cmd)]
                i = idx + len(cmd)
                continue

            # Запам'ятовуємо правильну відповідь (перший аргумент)
            correct_answer = args[0]

            # Перемішуємо відповіді
            shuffled = args.copy()
            random.shuffle(shuffled)

            # Знаходимо нову позицію правильної відповіді
            correct_idx = shuffled.index(correct_answer)
            correct_label = labels[correct_idx]
            answers.append(correct_label)

            task_num += 1

            # Формуємо нову команду
            new_cmd = cmd + ''.join(f'{{{a}}}' for a in shuffled)
            new_result += new_cmd

            i = end_pos

        result = new_result

    return result, answers

def process_file(filepath, answers_dict, topic_name):
    """Обробляє один файл і повертає кількість змін"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ❌ Помилка читання: {e}")
        return 0

    new_content, answers = shuffle_answers_and_track(content)

    if not answers:
        print(f"  ℹ️  Таблиць answerTable не знайдено")
        return 0

    # Зберігаємо відповіді
    if topic_name not in answers_dict:
        answers_dict[topic_name] = {}

    # Визначаємо базове ім'я файлу
    base_name = os.path.basename(filepath)
    answers_dict[topic_name][base_name] = answers

    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"  ✅ Перемішано {len(answers)} таблиць відповідей")
        return len(answers)
    except Exception as e:
        print(f"  ❌ Помилка запису: {e}")
        return 0

def generate_answers_tex(answers_dict, output_dir):
    """Генерує .tex файли з відповідями для кожної теми"""

    for topic_name, files in answers_dict.items():
        # Визначаємо директорію для збереження
        topic_dir = os.path.join(output_dir, topic_name)
        os.makedirs(topic_dir, exist_ok=True)

        # Об'єднуємо всі відповіді
        all_answers = []
        for file_name, file_answers in files.items():
            all_answers.extend(file_answers)

        if not all_answers:
            continue

        # Генеруємо .tex файл
        tex_content = generate_tex_answers(topic_name, all_answers)

        output_path = os.path.join(topic_dir, 'answers.tex')
        try:
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(tex_content)
            print(f"📄 Збережено відповіді: {output_path}")
        except Exception as e:
            print(f"❌ Помилка запису {output_path}: {e}")

def generate_tex_answers(topic_name, answers):
    """Генерує LaTeX код для відповідей"""

    # Розбиваємо на групи по 15 (для multicols)
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
    # Базова директорія
    base_dir = "/Users/markiyankharchuk/Desktop/НМТ_по_темах_латех"

    if len(sys.argv) > 1:
        base_dir = sys.argv[1]

    print(f"🔀 Рандомізація відповідей у файлах завдань НМТ")
    print(f"📁 Директорія: {base_dir}")
    print("=" * 60)

    # Словник для збору відповідей
    answers_dict = {}

    # Знаходимо всі .tex файли із завданнями
    files_processed = 0
    total_tables = 0

    # Паттерни файлів для обробки
    patterns = [
        "**/завдання.tex",
        "**/завдання*.tex",
        "generated/**/generated_tasks.tex",
        "generated/**/згенеровані.tex"
    ]

    processed_files = set()

    for pattern in patterns:
        from glob import glob
        for filepath in glob(os.path.join(base_dir, pattern), recursive=True):
            if filepath in processed_files:
                continue
            processed_files.add(filepath)

            # Визначаємо назву теми
            rel_path = os.path.relpath(filepath, base_dir)
            parts = rel_path.split(os.sep)

            if parts[0] == 'generated':
                topic_name = parts[1] if len(parts) > 1 else 'Інше'
            else:
                topic_name = parts[0] if len(parts) > 0 else 'Інше'

            print(f"\n📄 {rel_path}")

            tables = process_file(filepath, answers_dict, topic_name)
            total_tables += tables
            files_processed += 1

    print("\n" + "=" * 60)

    # Генеруємо файли відповідей
    print("\n📝 Генерація файлів відповідей...")

    # Для оригінальних тем - зберігаємо в ту ж директорію
    for topic_name, files in answers_dict.items():
        if topic_name.startswith('generated'):
            continue

        # Знаходимо директорію теми
        topic_dir = None
        for d in os.listdir(base_dir):
            if d.startswith(topic_name.split('.')[0]) or d == topic_name:
                topic_dir = os.path.join(base_dir, d)
                break

        if topic_dir and os.path.isdir(topic_dir):
            all_answers = []
            for file_answers in files.values():
                all_answers.extend(file_answers)

            if all_answers:
                tex_content = generate_tex_answers(topic_name, all_answers)
                output_path = os.path.join(topic_dir, 'відповіді.tex')
                try:
                    with open(output_path, 'w', encoding='utf-8') as f:
                        f.write(tex_content)
                    print(f"📄 Збережено: {output_path}")
                except Exception as e:
                    print(f"❌ Помилка: {e}")

    # Для згенерованих тем
    generated_dir = os.path.join(base_dir, 'generated')
    if os.path.exists(generated_dir):
        for topic_name, files in answers_dict.items():
            # Шукаємо теми в generated
            for gen_topic in os.listdir(generated_dir):
                if gen_topic == topic_name or topic_name.endswith(gen_topic):
                    gen_topic_dir = os.path.join(generated_dir, gen_topic)
                    if os.path.isdir(gen_topic_dir):
                        all_answers = []
                        for file_answers in files.values():
                            all_answers.extend(file_answers)

                        if all_answers:
                            tex_content = generate_tex_answers(gen_topic, all_answers)
                            output_path = os.path.join(gen_topic_dir, 'answers.tex')
                            try:
                                with open(output_path, 'w', encoding='utf-8') as f:
                                    f.write(tex_content)
                                print(f"📄 Оновлено: {output_path}")
                            except Exception as e:
                                print(f"❌ Помилка: {e}")
                        break

    # Зберігаємо JSON з усіма відповідями
    json_path = os.path.join(base_dir, 'answers_all.json')
    try:
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(answers_dict, f, ensure_ascii=False, indent=2)
        print(f"\n📊 Збережено JSON: {json_path}")
    except Exception as e:
        print(f"❌ Помилка збереження JSON: {e}")

    print("\n" + "=" * 60)
    print(f"📊 ПІДСУМОК:")
    print(f"   Оброблено файлів: {files_processed}")
    print(f"   Перемішано таблиць: {total_tables}")
    print(f"   Тем з відповідями: {len(answers_dict)}")
    print("\n💡 Тепер правильна відповідь розміщена випадково (А-Д)")

if __name__ == "__main__":
    random.seed()  # Випадковий seed для різних результатів
    main()
