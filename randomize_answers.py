#!/usr/bin/env python3
"""
Скрипт для рандомізації відповідей у файлах завдань НМТ.
Перемішує варіанти відповідей так, щоб правильна відповідь була на випадковій позиції (А-Д).
"""

import re
import random
import os
import sys

def shuffle_answer_table(match):
    """Перемішує відповіді в \answerTable{...}{...}{...}{...}{...}"""
    # Отримуємо всі 5 відповідей
    full_match = match.group(0)

    # Витягуємо вміст з фігурних дужок (обережно з вкладеними дужками)
    answers = []
    depth = 0
    current = ""
    in_args = False

    for char in full_match:
        if char == '{':
            depth += 1
            if depth == 1:
                in_args = True
                current = ""
            else:
                current += char
        elif char == '}':
            depth -= 1
            if depth == 0 and in_args:
                answers.append(current)
            else:
                current += char
        elif in_args and depth > 0:
            current += char

    if len(answers) != 5:
        return full_match  # Не змінюємо, якщо щось не так

    # Перемішуємо відповіді
    random.shuffle(answers)

    # Визначаємо тип команди
    if '\\answerTableBig' in full_match:
        cmd = '\\answerTableBig'
    elif '\\answerTableTall' in full_match:
        cmd = '\\answerTableTall'
    elif '\\answerTableSmall' in full_match:
        cmd = '\\answerTableSmall'
    else:
        cmd = '\\answerTable'

    return f"{cmd}{{{answers[0]}}}{{{answers[1]}}}{{{answers[2]}}}{{{answers[3]}}}{{{answers[4]}}}"

def shuffle_vertical_answers(match):
    """Перемішує відповіді у вертикальному форматі (\\textbf{А} & ...)"""
    full_match = match.group(0)

    # Шукаємо рядки з відповідями
    pattern = r'\\textbf\{([А-Д])\}\s*&\s*(.+?)(?=\\\\|$)'
    answers = re.findall(pattern, full_match, re.DOTALL)

    if len(answers) != 5:
        return full_match

    # Отримуємо тільки тексти відповідей
    answer_texts = [a[1].strip() for a in answers]
    random.shuffle(answer_texts)

    # Створюємо нові рядки
    labels = ['А', 'Б', 'В', 'Г', 'Д']
    new_lines = []
    for i, text in enumerate(answer_texts):
        new_lines.append(f"\\textbf{{{labels[i]}}} & {text} \\\\")

    # Замінюємо останній \\\\ на порожній рядок, якщо потрібно
    result = '\n'.join(new_lines)
    return result

def process_file(filepath):
    """Обробляє один файл"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ❌ Помилка читання: {e}")
        return False

    original_content = content

    # Патерни для різних типів таблиць відповідей
    patterns = [
        r'\\answerTableBig\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}',
        r'\\answerTableTall\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}',
        r'\\answerTableSmall\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}',
        r'\\answerTable\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}\{[^}]*(?:\{[^}]*\}[^}]*)*\}',
    ]

    changes = 0
    for pattern in patterns:
        matches = list(re.finditer(pattern, content))
        for m in reversed(matches):  # В зворотньому порядку, щоб не зміщувати позиції
            old = m.group(0)
            new = shuffle_answer_table(m)
            if old != new:
                content = content[:m.start()] + new + content[m.end():]
                changes += 1

    if changes > 0:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(content)
            print(f"  ✅ Змінено {changes} таблиць відповідей")
            return True
        except Exception as e:
            print(f"  ❌ Помилка запису: {e}")
            return False
    else:
        print(f"  ℹ️  Змін не потрібно")
        return False

def main():
    # Базова директорія
    base_dir = "/Users/markiyankharchuk/Desktop/НМТ_по_темах_латех"

    if len(sys.argv) > 1:
        base_dir = sys.argv[1]

    print(f"🔍 Шукаю файли в: {base_dir}")
    print("=" * 60)

    # Знаходимо всі файли завдання.tex
    files_processed = 0
    files_changed = 0

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file == "завдання.tex":
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, base_dir)
                print(f"\n📄 {rel_path}")

                if process_file(filepath):
                    files_changed += 1
                files_processed += 1

    print("\n" + "=" * 60)
    print(f"📊 Оброблено файлів: {files_processed}")
    print(f"✅ Змінено файлів: {files_changed}")

if __name__ == "__main__":
    random.seed()  # Використовуємо випадковий seed
    main()
