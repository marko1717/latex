# -*- coding: utf-8 -*-
"""Рисунок до завдання через OpenAI Images API -- автономний скрипт (один файл, без бази й маніфесту).

Можна скопіювати в будь-яку гілку чи репозиторій. Потрібен лише Python 3; Pillow -- для обробки
(обрізати поля, зменшити, стиснути, перевірити прозорість): pip3 install pillow.
Без Pillow зберігається сире зображення.

Ключ API береться ТІЛЬКИ зі змінної середовища OPENAI_API_KEY (export у ~/.zshrc) і ніде не друкується.

    python3 рисунок_api.py перевірити
        безкоштовно: чи робочий ключ і які моделі зображень доступні проєкту

    python3 рисунок_api.py згенерувати "опис англійською" тека/nmt_kefir.png [параметри]
        --прозорий            прозорий фон (PNG) -- для предметів, поверх яких TikZ малює підписи
        --формат 1024x1536    1024x1024 (типово), 1024x1536 (вертикальний), 1536x1024 (горизонтальний), auto
        --якість medium       low (чернетка, найдешевше) | medium (типово) | high | auto
                              (xhigh, max -- лише моделі gpt-image-2.5)
        --скільки 3           кілька варіантів за один запит -> nmt_kefir_1.png, nmt_kefir_2.png ...
        --ширина 900          ширина готового PNG у пікселях (типово 1000)
        --без-стилю           не додавати стильову приставку (для «фото»: опишіть стиль у самому описі)
        --без-обробки         лишити тільки сире зображення
        --модель ID           модель явно (інакше -- змінна OPENAI_IMAGE_MODEL або автоматичний вибір)
        --лише-запит          нічого не надсилати: показати тіло запиту (безкоштовно)

    python3 рисунок_api.py обробити сирий.png готовий.png [--ширина 900] [--прозорий]
        обробити вже наявне зображення (обрізати поля, зменшити, стиснути)

Що записується для «тека/nmt_kefir.png»:
    тека/nmt_kefir_raw.png   сире зображення від API (у LaTeX не вставляти, у git не комітити)
    тека/nmt_kefir.png       готове: обрізане, зменшене, стиснуте -- його й вставляють у LaTeX
    тека/nmt_kefir.json      опис, модель, розмір, дата, ціна -- щоб повторити чи перегенерувати

Правило: генератор малює лише «картинку» (предмет, пейзаж, фото) без тексту, чисел і всього, від
чого залежить відповідь. Кількості, підписи кирилицею, точки, кути й відрізки накладає TikZ.
"""
import os, sys, json, time, base64, argparse, datetime, urllib.request, urllib.error

API = "https://api.openai.com/v1"
# у такому порядку модель вибирається автоматично (перша, яка є в проєкті й не має дати вимкнення)
БАЖАНІ_МОДЕЛІ = ("gpt-image-2-2026-04-21", "gpt-image-2", "gpt-image-2.5-flare", "gpt-image-2.5-sunburst")
СТИЛЬ = ("Clean flat vector illustration for a school math exam booklet, soft muted colors, "
         "no text, no letters, no numbers, no labels, no watermark, no border, simple shapes, ")
СТИЛЬ_БІЛИЙ = "white background, the object centered with generous empty margins. "
# для прозорого фону опис важливіший за параметр background: не згадувати тло, просити ізольований предмет
СТИЛЬ_ПРОЗОРИЙ = "a single isolated object on a fully transparent background, no background scene, no shadow, no checkerboard. "
# 429, які повтор не лікує: закінчилися кошти або досягнуто ліміту витрат
ГРОШІ = ("insufficient_quota", "credit_balance_exhausted", "organization_spend_limit_exceeded",
         "project_spend_limit_exceeded", "organization_usage_limit_exceeded", "billing_hard_limit_reached")


def ключ():
    k = os.environ.get("OPENAI_API_KEY", "").strip()
    if not k:
        raise SystemExit("немає змінної OPENAI_API_KEY.\n"
                         "Додайте в ~/.zshrc рядок  export OPENAI_API_KEY=\"sk-...\"  і відкрийте новий термінал\n"
                         "(у Claude Code запускайте так: zsh -ic 'python3 рисунок_api.py ...').")
    return k


def запит(path, key, body=None, timeout=300):
    data = json.dumps(body).encode("utf-8") if body is not None else None
    headers = {"Authorization": "Bearer " + key}
    if data is not None: headers["Content-Type"] = "application/json"
    req = urllib.request.Request(API + path, data=data, headers=headers)
    with urllib.request.urlopen(req, timeout=timeout) as r:
        return json.load(r)


def розібрати_помилку(e):
    """HTTPError -> (код, тип, повідомлення) з JSON {"error": {...}} відповіді OpenAI"""
    raw = e.read().decode("utf-8", "replace")
    try:
        err = json.loads(raw).get("error") or {}
    except ValueError:
        err = {}
    return (err.get("code") or ""), (err.get("type") or ""), (err.get("message") or raw[:400])


def пояснення(status, code, typ, msg):
    if status == 401:
        return "ключ не прийнято (401): перевірте OPENAI_API_KEY -- без пробілів і зайвих символів, ключ не відкликано.\n" + msg
    if status == 403 and "verif" in msg.lower():
        return ("організацію не верифіковано (403): для моделей gpt-image потрібна верифікація -- "
                "platform.openai.com -> Settings -> Organization -> General -> Verify Organization. "
                "Після верифікації доступ вмикається не одразу (від 15 хв до доби).\n" + msg)
    if status == 403:
        return "доступ заборонено (403):\n" + msg
    if status == 429 and (code in ГРОШІ or typ == "insufficient_quota"):
        return ("закінчилися кошти або досягнуто ліміту витрат (429, %s): поповніть Billing або підніміть "
                "ліміт у Settings -> Limits; повтор запиту тут не допоможе.\n%s" % (code or typ, msg))
    if status == 429:
        return "забагато запитів (429): зачекайте хвилину й повторіть.\n" + msg
    if status == 400 and (code == "moderation_blocked" or typ == "image_generation_user_error"):
        return "опис відхилив фільтр безпеки (400, %s): переформулюйте опис.\n%s" % (code or typ, msg)
    if status == 400:
        return "запит відхилено (400) -- неприпустимий параметр (розмір, якість, модель?):\n" + msg
    return "OpenAI повернув помилку %d:\n%s" % (status, msg)


def моделі_зображень(key):
    """моделі gpt-image проєкту; ті, що мають дату вимкнення, -- наприкінці"""
    ms = [m for m in запит("/models", key, timeout=60)["data"] if m["id"].startswith("gpt-image")]
    def вага(m):
        i = m["id"]
        return (bool(m.get("shutdown_date")), БАЖАНІ_МОДЕЛІ.index(i) if i in БАЖАНІ_МОДЕЛІ else len(БАЖАНІ_МОДЕЛІ), i)
    return sorted(ms, key=вага)


def перевірити():
    try:
        ms = моделі_зображень(ключ())
    except urllib.error.HTTPError as e:
        raise SystemExit(пояснення(e.code, *розібрати_помилку(e)))
    print("ключ робочий; моделі зображень:",
          ", ".join(m["id"] + (" (вимкнуть %s)" % m["shutdown_date"] if m.get("shutdown_date") else "") for m in ms) or "немає")
    if ms: print("типово буде використано:", ms[0]["id"])
    print("(верифікацію організації це не перевіряє: якщо її немає, 403 з'явиться під час генерації)")


def імена(out, n):
    stem, ext = os.path.splitext(out)
    if ext.lower() != ".png": raise SystemExit("вихідний файл має бути .png: %s" % out)
    if any(ord(c) > 127 for c in os.path.basename(stem)):
        print("  ! ім'я файлу з не-ASCII символами: LaTeX і Overleaf надійніше працюють з латиницею (напр. nmt_kefir.png)")
    return [stem] if n == 1 else ["%s_%d" % (stem, i) for i in range(1, n + 1)]


def тіло(a, model):
    стиль = "" if a.без_стилю else СТИЛЬ + (СТИЛЬ_ПРОЗОРИЙ if a.прозорий else СТИЛЬ_БІЛИЙ)
    body = {"model": model, "prompt": стиль + a.опис, "size": a.формат, "quality": a.якість, "n": a.скільки}
    if a.прозорий: body["background"] = "transparent"; body["output_format"] = "png"
    return body


def ціна(model, usage):
    """орієнтовно, $: gpt-image-2 і 2.5 -- $30 за 1M вихідних токенів зображення, $5 за 1M вхідних текстових"""
    if not usage or not model.startswith("gpt-image-2"): return None
    text_in = (usage.get("input_tokens_details") or {}).get("text_tokens", usage.get("input_tokens", 0))
    return usage.get("output_tokens", 0) * 30e-6 + text_in * 5e-6


def згенерувати(a):
    model = a.модель or os.environ.get("OPENAI_IMAGE_MODEL") or os.environ.get("NMT_IMAGE_MODEL")
    stems = імена(a.файл, a.скільки)
    if a.якість in ("xhigh", "max") and model and not model.startswith("gpt-image-2.5"):
        raise SystemExit("якість %s є лише в моделей gpt-image-2.5-*" % a.якість)
    if a.лише_запит:
        print(json.dumps(тіло(a, model or "(буде вибрано автоматично)"), ensure_ascii=False, indent=1)); return
    key = ключ()
    if not model:
        try: ms = моделі_зображень(key)
        except urllib.error.HTTPError as e: raise SystemExit(пояснення(e.code, *розібрати_помилку(e)))
        if not ms: raise SystemExit("проєкту не доступна жодна модель gpt-image")
        model = ms[0]["id"]
    body = тіло(a, model)
    os.makedirs(os.path.dirname(os.path.abspath(a.файл)), exist_ok=True)
    print("запит до %s (%s, %s%s, %d шт.) ..." % (model, a.формат, a.якість, ", прозорий фон" if a.прозорий else "", a.скільки))
    for attempt in range(6):
        try:
            data = запит("/images/generations", key, body); break
        except urllib.error.HTTPError as e:
            code, typ, msg = розібрати_помилку(e)
            if e.code == 429 and (code in ГРОШІ or typ == "insufficient_quota"): повтор = False
            elif e.code == 403: повтор = "verif" in msg.lower() and attempt < 2     # доступ після верифікації вмикається не одразу
            else: повтор = e.code in (429, 500, 502, 503, 504) and attempt < 5
            if not повтор: raise SystemExit(пояснення(e.code, code, typ, msg))
            wait = 15 * (attempt + 1)
            try: wait = max(wait, min(60, int(e.headers.get("Retry-After", 0))))
            except (TypeError, ValueError): pass
            print("  OpenAI: %d %s, повтор через %d с" % (e.code, code, wait)); time.sleep(wait)
        except urllib.error.URLError as e:
            if attempt < 5: print("  мережа: %s, повтор" % e.reason); time.sleep(10); continue
            raise SystemExit("немає зʼєднання з api.openai.com: %s" % e.reason)
    if a.прозорий and data.get("background") == "opaque":
        print("  ! модель повернула непрозорий фон: приберіть з опису згадки про тло чи сцену й повторіть")
    usd = ціна(model, data.get("usage"))
    for stem, item in zip(stems, data["data"]):
        raw = stem + "_raw.png"
        open(raw, "wb").write(base64.b64decode(item["b64_json"]))
        print("сире:", raw)
        if a.прозорий: перевірити_прозорість(raw)
        if not a.без_обробки: обробити_файл(raw, stem + ".png", a.ширина, a.прозорий)
        json.dump(dict(опис=a.опис, стиль=not a.без_стилю, модель=model, формат=a.формат, якість=a.якість,
                       прозорий=a.прозорий, дата=datetime.date.today().isoformat(),
                       ціна_usd=round(usd / max(1, len(stems)), 4) if usd is not None else None),
                  open(stem + ".json", "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    if usd is not None: print("орієнтовна ціна запиту: $%.3f" % usd)


def перевірити_прозорість(path):
    try:
        from PIL import Image
    except ImportError:
        return
    im = Image.open(path)
    if im.mode not in ("RGBA", "LA") or im.getchannel("A").getextrema()[0] == 255:
        print("  ! у зображенні немає прозорих ділянок: спробуйте ще раз або змініть опис (без тла)")


def обробити_файл(src, out, max_w=1000, прозорий=False):
    """обрізати порожні поля (прозорі або білі), зменшити до max_w, стиснути палітрою"""
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    try:
        from PIL import Image, ImageChops
    except ImportError:
        import shutil; shutil.copyfile(src, out)
        print("  ! немає Pillow (pip3 install pillow) -- скопійовано без обробки:", out); return out
    im = Image.open(src)
    if прозорий and im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA"); box = im.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
    else:
        if im.mode in ("RGBA", "LA", "P"):          # прозорі ділянки -> білі (інакше після convert("RGB") вони чорні)
            im = im.convert("RGBA"); bg = Image.new("RGBA", im.size, (255, 255, 255, 255)); bg.alpha_composite(im); im = bg
        im = im.convert("RGB")
        box = ImageChops.difference(im, Image.new("RGB", im.size, (255, 255, 255))).convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()
    if box:
        pad = int(0.02 * max(im.size))
        im = im.crop((max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad)))
    if im.width > max_w: im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    if im.mode == "RGBA": im.quantize(colors=256, method=Image.Quantize.FASTOCTREE).save(out, optimize=True)
    else: im.quantize(colors=192, method=Image.Quantize.MEDIANCUT).save(out, optimize=True)
    print("готове: %s (%dx%d, %d КБ)" % (out, im.width, im.height, os.path.getsize(out) // 1024))
    return out


def main():
    ap = argparse.ArgumentParser(description="рисунок через OpenAI Images API", formatter_class=argparse.RawDescriptionHelpFormatter, epilog=__doc__)
    sub = ap.add_subparsers(dest="cmd")
    sub.add_parser("перевірити", help="безкоштовно перевірити ключ і доступні моделі")
    g = sub.add_parser("згенерувати", help="створити зображення за описом")
    g.add_argument("опис"); g.add_argument("файл")
    g.add_argument("--прозорий", action="store_true")
    g.add_argument("--формат", default="1024x1024")
    g.add_argument("--якість", default="medium", choices=["low", "medium", "high", "auto", "xhigh", "max"])
    g.add_argument("--скільки", type=int, default=1)
    g.add_argument("--ширина", type=int, default=1000)
    g.add_argument("--без-стилю", dest="без_стилю", action="store_true")
    g.add_argument("--без-обробки", dest="без_обробки", action="store_true")
    g.add_argument("--модель")
    g.add_argument("--лише-запит", dest="лише_запит", action="store_true")
    o = sub.add_parser("обробити", help="обрізати, зменшити й стиснути наявне зображення")
    o.add_argument("сирий"); o.add_argument("готовий")
    o.add_argument("--ширина", type=int, default=1000)
    o.add_argument("--прозорий", action="store_true")
    a = ap.parse_args()
    if a.cmd == "перевірити": перевірити()
    elif a.cmd == "згенерувати":
        if not 1 <= a.скільки <= 10: raise SystemExit("--скільки: від 1 до 10")
        згенерувати(a)
    elif a.cmd == "обробити": обробити_файл(a.сирий, a.готовий, a.ширина, a.прозорий)
    else: ap.print_help()


if __name__ == "__main__":
    main()
