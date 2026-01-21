#!/usr/bin/env python3
"""
Скрипт для рандомізації відповідей у файлах завдань НМТ.
Версія 2: правильно обробляє вкладені дужки та складні LaTeX вирази.
"""

import re
import random
import os
import sys

def extract_braced_args(text, start_pos, num_args=5):
    """
    Витягує num_args аргументів у фігурних дужках, починаючи з позиції start_pos.
    Правильно обробляє вкладені дужки.
    Повертає (список_аргументів, кінцева_позиція) або (None, start_pos) якщо не вдалося.
    """
    args = []
    pos = start_pos

    for _ in range(num_args):
        # Пропускаємо пробіли
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

def shuffle_answers_in_content(content):
    """
    Знаходить всі виклики answerTable* та перемішує відповіді.
    """
    # Патерни команд
    commands = ['\\answerTableBig', '\\answerTableTall', '\\answerTableSmall', '\\answerTable']

    changes = 0
    result = content

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
            # (наприклад, \answerTable не повинна захоплювати \answerTableBig)
            is_exact = True
            if cmd == '\\answerTable':
                # Перевіряємо, чи немає далі Big/Tall/Small
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

            # Перемішуємо відповіді
            random.shuffle(args)
            changes += 1

            # Формуємо нову команду
            new_cmd = cmd + ''.join(f'{{{a}}}' for a in args)
            new_result += new_cmd

            i = end_pos

        result = new_result

    return result, changes

def process_file(filepath):
    """Обробляє один файл"""
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
    except Exception as e:
        print(f"  ❌ Помилка читання: {e}")
        return False, 0

    new_content, changes = shuffle_answers_in_content(content)

    if changes > 0:
        try:
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(new_content)
            print(f"  ✅ Перемішано {changes} таблиць відповідей")
            return True, changes
        except Exception as e:
            print(f"  ❌ Помилка запису: {e}")
            return False, 0
    else:
        print(f"  ℹ️  Таблиць answerTable не знайдено")
        return False, 0

def main():
    # Базова директорія
    base_dir = "/Users/markiyankharchuk/Desktop/НМТ_по_темах_латех"

    if len(sys.argv) > 1:
        base_dir = sys.argv[1]

    print(f"🔀 Рандомізація відповідей у файлах завдань НМТ")
    print(f"📁 Директорія: {base_dir}")
    print("=" * 60)

    # Знаходимо всі файли завдання.tex
    files_processed = 0
    files_changed = 0
    total_tables = 0

    for root, dirs, files in os.walk(base_dir):
        for file in files:
            if file == "завдання.tex":
                filepath = os.path.join(root, file)
                rel_path = os.path.relpath(filepath, base_dir)
                print(f"\n📄 {rel_path}")

                changed, tables = process_file(filepath)
                if changed:
                    files_changed += 1
                    total_tables += tables
                files_processed += 1

    print("\n" + "=" * 60)
    print(f"📊 ПІДСУМОК:")
    print(f"   Оброблено файлів: {files_processed}")
    print(f"   Змінено файлів: {files_changed}")
    print(f"   Перемішано таблиць: {total_tables}")
    print("\n💡 Тепер правильна відповідь розміщена випадково (А-Д)")

if __name__ == "__main__":
    random.seed()  # Випадковий seed для різних результатів
    main()
