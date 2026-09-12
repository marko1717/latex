# NMT Task Generator (Math Quest)

This project automates the creation of mathematical problems for the Ukrainian NMT (National Multi-subject Test). It uses Python to generate unique versions of tasks based on templates reverse-engineered from real exam questions.

## 🎯 Goals
*   Generate **5000+ unique tasks** for training.
*   Cover all NMT math topics (Algebra, Geometry, Statistics).
*   Output ready-to-print LaTeX documents compatible with Overleaf.

## 🛠 Usage

1.  **Clone the repo**:
    ```bash
    git clone https://github.com/marko1717/latex.git
    cd latex
    ```

2.  **Generate Tasks**:
    Run the generation script. This will create clean LaTeX files in the `tex/` directory.
    ```bash
    PYTHONPATH=. python3 scripts/generate_overleaf_doc.py
    ```

3.  **View Results**:
    Open `tex/arithmetic_progression.tex` or `tex/geometric_progression.tex`. You can compile them with any LaTeX editor or upload to Overleaf.

## 📚 Topics Covered
*   **Arithmetic Progression**: $d$, $S_n$, term properties, word problems, diagrams.
*   **Geometric Progression**: $q$, $S_n$, growth problems, formulas.

## 🤝 Contributing
See [CONTRIBUTING.md](CONTRIBUTING.md) for instructions on how to add new task types.

---

## 📚 База завдань НМТ 2022--2026 по темах (єдиний формат)

Усі завдання основних сесій НМТ 2023--2026 (а також окремі завдання додаткових сесій
2023 і 2025 років та три завдання демоваріанта 2022 року) зібрано **по темах** в одному форматі запису
(формат збірника НМТ-2026: шрифт Schoolbook, макроси `\zadtask`, `\zadnum`, `\answerTable`,
`\answerTableTall`, `\matchingGrid`, `\nmtAnswerBox`, `\nmtyear{...}`).

* `<N>. <Тема>/завдання.tex` --- самостійний документ теми (XeLaTeX/LuaLaTeX). Усередині завдання
  згруповано за **типом**: спочатку тестові з вибором однієї відповіді (А--Д), далі на встановлення
  відповідності, далі з короткою відповіддю (`\typeTitle{...}`); у межах типу --- за роками (2023 → 2026),
  рік кожного завдання позначено міткою `\nmtyear{...}` праворуч від умови; нумерація наскрізна.
  Теми 28 і 30 мають по два файли (рівняння / функція і вирази; вирази / функція).
* Теми згруповано у **6 розділів** (як у збірнику НМТ-2026): 1 Числа і вирази (теми 1--5, 7, 26, 30-вирази);
  2 Рівняння і нерівності, включно з параметрами (6, 8, 9, 19, 22, 23, 27, 28-рівняння, 29, 31, 32, 43);
  3 Функції, включно з прогресіями, похідною, первісною (20, 21, 24, 25, 28-функція, 30-функція, 33, 34);
  4 Планіметрія (10--17); 5 Стереометрія (18, 38--42); 6 Комбінаторика, теорія ймовірності, статистика (35--37).
* `НМТ_2023-2026_всі_теми.tex` --- master-документ: усі розділи й теми в одному PDF (пакет `docmute`);
  `Розділ_1_….tex` … `Розділ_6_….tex` --- те саме окремо по розділах.
* `Schoolbook-*.otf` --- шрифти формату 2026 (лежать у корені; шлях у преамбулі підбирається автоматично).
* `archive/старий_формат/` --- старі файли 2023--2025 (старий преамбул), джерело для збірки.
* `archive/джерела_2026/` --- копії джерел 2026: `збірник/оригінали` (тиждень 1 по розділах), `збірник/розділи`
  (розв'язки), `збірник/збірник_НМТ_тиждень.tex` (3.06 №5), `сесії/<дата>/завдання.tex` (повні варіанти 8.06--19.06).
* `scripts/data/originals_2026.json` --- оригінали НМТ-2026 (17 сесій 23.05--19.06, 373 завдання; 2.06 №14 немає в жодному джерелі),
  витягнуті скриптом `scripts/extract_2026_originals.py` із `archive/джерела_2026/`.
* `scripts/data/topics_2026.json` --- розподіл завдань 2026 за темами (`"2026-<сесія>-<№>": ["<тема>", ...]`);
  перша тема основна, решта --- додаткові (завдання дублюється в кілька тем).
* `scripts/build_nmt_2023_2026.py` --- збірка: конвертує старі файли в новий формат і додає завдання 2026.
* `scripts/звірка_pdf_2023_2025/` --- звірка бази з посібником «НМТ 2023--2025» (55 сесій, 1183 завдання)
  і `scripts/звірка_тематичний_збірник/` --- із тематичним збірником «Числа і вирази» (234 завдання);
  у кожній папці README з методикою і звіт про те, чого бракувало.

```bash
python3 scripts/build_nmt_2023_2026.py      # перезібрати всі 45 файлів + master
```

### Дві гілки: `main` для Overleaf, `джерела` для збірки

Overleaf обмежує сумарний розмір текстових файлів проєкту, тож у гілці **`main`**
лежить тільки те, що потрібно для компіляції: файли тем, master, розділи, шрифти,
шаблон і скрипти (≈3 МБ тексту).

Архів джерел і службові дані (`archive/`, `scripts/data/`, а також старі теки
генератора `generated/`, `tex/`, `generators/`, `analysis_2025/`, `nmt_database.json`)
лежать у гілці **`джерела`**. На диску вони нікуди не діваються --- у `main` їх просто
не відстежує git (див. `.gitignore`), тому перезбірка бази працює як і раніше.

```bash
git push origin main              # Overleaf тягне саме цю гілку
git checkout джерела              # подивитися/оновити архів джерел
git branch -f джерела main-і-архів  # оновити гілку джерел після змін в архіві
```

Щоб виправити тему якогось завдання 2026 --- відредагуйте `scripts/data/topics_2026.json` і перезберіть.
Розв'язки й відповіді до завдань 2026 (там, де вони відомі) вбудовано у файли, але приховано:
у преамбулі замініть `\showsolutionsfalse` на `\showsolutionstrue`.
Дата сесії 2026 і відповідь до кожного завдання записані у коментарях TeX поряд із завданням.
