# -*- coding: utf-8 -*-
"""Рисунки-ілюстрації до завдань через OpenAI Images API.

Генератор зображень малює лише «картинку» (предмет, пейзаж, фото), без тексту й без того,
від чого залежить відповідь. Усе точне -- кількості, підписи кирилицею, лінії, кути -- накладає
TikZ поверх зображення в самому завданні. Кожне зображення переглядається перед вставлянням.

Опис рисунків -- у scripts/data/рисунки.json:
  {"id": "kefir", "тека": "2.відсотки, арифметичні задачі, подільність",
   "промпт": "...", "формат": "1024x1536", "стан": "потрібно|згенеровано|прийнято"}

    python3 scripts/рисунки.py перевірити                # чи робочий ключ (безкоштовно)
    python3 scripts/рисунки.py список
    python3 scripts/рисунки.py згенерувати kefir         # потрібна змінна середовища OPENAI_API_KEY
    python3 scripts/рисунки.py обробити kefir            # обрізати поля, зменшити, покласти в теку теми

Ключ API скрипт бере тільки зі змінної середовища і ніде його не друкує й не записує.
"""
import os, sys, json, base64, urllib.request, urllib.error, unicodedata

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MANIFEST = os.path.join(ROOT, "scripts", "data", "рисунки.json")
ВХІДНІ = os.path.join(ROOT, "рисунки_вхідні")          # сирі зображення (у git не йдуть)
МОДЕЛЬ = os.environ.get("NMT_IMAGE_MODEL", "gpt-image-1")

СТИЛЬ = ("Clean flat vector illustration for a school math exam booklet, soft muted colors, "
         "white background, no text, no letters, no numbers, no labels, no watermark, no border, "
         "simple shapes, the object centered with generous empty margins. ")


def завантажити():
    return json.load(open(MANIFEST, encoding="utf-8")) if os.path.exists(MANIFEST) else []


def зберегти(items):
    json.dump(items, open(MANIFEST, "w", encoding="utf-8"), ensure_ascii=False, indent=1)


def знайти(items, id_):
    for it in items:
        if it["id"] == id_: return it
    raise SystemExit("немає рисунка %s у %s" % (id_, MANIFEST))


def згенерувати(it):
    key = os.environ.get("OPENAI_API_KEY")
    if not key:
        raise SystemExit("немає змінної OPENAI_API_KEY -- додайте її в ~/.zshrc (export OPENAI_API_KEY=...) і відкрийте новий термінал")
    body = {"model": МОДЕЛЬ, "prompt": (СТИЛЬ if it.get("стиль", True) else "") + it["промпт"],
            "size": it.get("формат", "1024x1024"), "n": 1}
    if МОДЕЛЬ.startswith("gpt-image"):
        body["quality"] = it.get("якість", "medium")
        if it.get("фон") == "прозорий": body["background"] = "transparent"; body["output_format"] = "png"
    req = urllib.request.Request("https://api.openai.com/v1/images/generations", data=json.dumps(body).encode("utf-8"),
                                 headers={"Authorization": "Bearer " + key, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=300) as r: data = json.load(r)
    except urllib.error.HTTPError as e:
        msg = e.read().decode("utf-8", "replace")[:500]
        raise SystemExit("OpenAI повернув помилку %d: %s" % (e.code, msg))
    os.makedirs(ВХІДНІ, exist_ok=True)
    n = sum(1 for f in os.listdir(ВХІДНІ) if f.startswith(it["id"] + "_")) + 1
    path = os.path.join(ВХІДНІ, "%s_%02d.png" % (it["id"], n))
    open(path, "wb").write(base64.b64decode(data["data"][0]["b64_json"]))
    it["стан"] = "згенеровано"; it.setdefault("спроби", []).append(os.path.basename(path))
    print("записано", path)
    return path


def обробити(it, src=None, max_w=1400):
    """обрізати білі поля, зменшити, зберегти PNG у теці теми під іменем id.png"""
    from PIL import Image, ImageChops
    src = src or os.path.join(ВХІДНІ, it["спроби"][-1])
    im = Image.open(src)
    if im.mode in ("RGBA", "LA") and it.get("фон") == "прозорий":
        im = im.convert("RGBA"); box = im.split()[-1].point(lambda v: 255 if v > 20 else 0).getbbox()
    else:
        im = im.convert("RGB")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        box = ImageChops.difference(im, bg).convert("L").point(lambda v: 255 if v > 12 else 0).getbbox()
    if box:
        pad = int(0.02 * max(im.size))
        box = (max(0, box[0] - pad), max(0, box[1] - pad), min(im.width, box[2] + pad), min(im.height, box[3] + pad))
        im = im.crop(box)
    if im.width > max_w: im = im.resize((max_w, round(im.height * max_w / im.width)), Image.LANCZOS)
    folder = os.path.join(ROOT, unicodedata.normalize("NFC", it["тека"]))
    if not os.path.isdir(folder):
        folder = next(os.path.join(ROOT, d) for d in os.listdir(ROOT) if unicodedata.normalize("NFC", d) == unicodedata.normalize("NFC", it["тека"]))
    out = os.path.join(folder, it["id"] + ".png")
    if im.mode == "RGBA": im.save(out, optimize=True)
    else: im.quantize(colors=128, method=Image.Quantize.MEDIANCUT).save(out, optimize=True)
    it["стан"] = "прийнято"; it["файл"] = os.path.relpath(out, ROOT)
    print("записано", out, "%d КБ" % (os.path.getsize(out) // 1024))
    return out


def перевірити():
    """безкоштовний запит (список моделей): чи ключ робочий. Сам ключ не друкується."""
    key = os.environ.get("OPENAI_API_KEY", "")
    if not key: raise SystemExit("змінна OPENAI_API_KEY не задана")
    req = urllib.request.Request("https://api.openai.com/v1/models", headers={"Authorization": "Bearer " + key})
    try:
        with urllib.request.urlopen(req, timeout=60) as r: ids = [m["id"] for m in json.load(r)["data"]]
    except urllib.error.HTTPError as e:
        raise SystemExit("ключ не прийнято: HTTP %d" % e.code)
    img = sorted(i for i in ids if "image" in i or "dall" in i)
    print("ключ робочий; моделі зображень:", ", ".join(img) or "немає")


def main():
    cmd = sys.argv[1] if len(sys.argv) > 1 else "список"
    if cmd == "перевірити": return перевірити()
    items = завантажити()
    if cmd == "список":
        for it in items: print("%-20s %-12s %s" % (it["id"], it.get("стан", "?"), it["промпт"][:80]))
        return
    it = знайти(items, sys.argv[2])
    if cmd == "згенерувати": згенерувати(it)
    elif cmd == "обробити": обробити(it, sys.argv[3] if len(sys.argv) > 3 else None)
    else: raise SystemExit(__doc__)
    зберегти(items)


if __name__ == "__main__":
    main()
