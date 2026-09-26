# -*- coding: utf-8 -*-
"""Картинки питань ClassTime з експорту користувача -> локальне/classtime/ (у git не йде).

Експорт (questions_enriched.json) зроблено раніше з акаунта користувача; тут лише качаються
його ж картинки з CDN images.classtime.com за посиланнями з експорту. Повторний запуск
докачує тільки відсутні.

    python3 scripts/classtime/картинки.py [шлях/до/questions_enriched.json]
"""
import os, sys, json, glob, time, threading, urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
ДАНІ = os.path.join(ROOT, "локальне", "classtime")
КАРТИНКИ = os.path.join(ДАНІ, "картинки")
UA = "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126 Safari/537.36"
ПОТОКІВ, ПАУЗА = 4, 0.2


def знайти_експорт():
    for p in glob.glob(os.path.expanduser("~/Desktop/*/LearningPlatform/objective-germain/classtime-export/questions_enriched.json")):
        return p
    raise SystemExit("не знайдено questions_enriched.json -- передайте шлях аргументом")


def вже_є(image_id):
    return any(os.path.exists(os.path.join(КАРТИНКИ, image_id + e)) for e in (".jpg", ".png", ".gif", ".webp"))


def main():
    src = sys.argv[1] if len(sys.argv) > 1 else знайти_експорт()
    q = json.load(open(src, encoding="utf-8"))
    os.makedirs(КАРТИНКИ, exist_ok=True)
    json.dump(q, open(os.path.join(ДАНІ, "питання.json"), "w", encoding="utf-8"), ensure_ascii=False)   # копія експорту поруч
    urls = {}
    for x in q:
        if x.get("imageId") and x.get("imageUrl"): urls[x["imageId"]] = x["imageUrl"]
    todo = [(i, u) for i, u in sorted(urls.items()) if not вже_є(i)]
    print("унікальних картинок: %d, докачати: %d" % (len(urls), len(todo)), flush=True)
    lock, done, failed = threading.Lock(), [0], []

    def one(item):
        i, u = item
        for attempt in range(4):
            try:
                req = urllib.request.Request(u, headers={"User-Agent": UA})
                with urllib.request.urlopen(req, timeout=60) as r:
                    data, ctype = r.read(), (r.headers.get("Content-Type") or "")
                ext = ".png" if "png" in ctype else ".gif" if "gif" in ctype else ".webp" if "webp" in ctype else ".jpg"
                open(os.path.join(КАРТИНКИ, i + ext), "wb").write(data)
                break
            except (urllib.error.URLError, TimeoutError) as e:
                if attempt == 3:
                    with lock: failed.append((i, str(e)))
                time.sleep(5 * (attempt + 1))
        time.sleep(ПАУЗА)
        with lock:
            done[0] += 1
            if done[0] % 500 == 0: print("  %d/%d" % (done[0], len(todo)), flush=True)

    with ThreadPoolExecutor(ПОТОКІВ) as ex: list(ex.map(one, todo))
    json.dump(failed, open(os.path.join(ДАНІ, "не_завантажено.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=1)
    print("готово; не вдалося: %d" % len(failed), flush=True)


if __name__ == "__main__":
    main()
