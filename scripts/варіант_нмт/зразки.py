# -*- coding: utf-8 -*-
"""База зразків для подальшого використання: усі джерела в одному файлі з однаковими полями.

Джерела (дублікати між ними зведено в один запис):
  база НМТ          -- варіант_каталог.json + блоки тем (LaTeX, перевірені відповіді й категорії)
  ЗНО офіційні      -- локальне/зно_офіційні/завдання/*.json (перенабрані зошити УЦОЯО)
  osvita            -- локальне/osvita/завдання.json (текст з формулами; лише зразки, не для поширення)
  ClassTime         -- локальне/classtime/каталог.json (картинка + розпізнаний текст + відповідь)

    python3 scripts/варіант_нмт/зразки.py      # -> локальне/зразки.json + підсумок за слотами
Файл лежить у «локальне» (поза git), бо містить матеріали osvita й ClassTime.
"""
import os, re, sys, json, glob, collections

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.dirname(os.path.dirname(HERE))
sys.path.insert(0, HERE)
import спільне as S                                    # noqa: E402

ЛОКАЛЬНЕ = os.path.join(ROOT, "локальне")
ВИХІД = os.path.join(ЛОКАЛЬНЕ, "зразки.json")


def завантажити(p, default=None):
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


def main():
    зразки, пропущено = [], collections.Counter()

    # 1. база НМТ (основне джерело: перевірені відповіді й категорії)
    blocks = {t["id"]: t["блок"] for t in S.завдання_бази()}
    cat = [json.loads(l.strip().rstrip(",")) for l in open(S.КАТАЛОГ, encoding="utf-8") if l.strip().startswith("{")]
    for r in cat:
        if r["id"] not in blocks: continue
        зразки.append(dict(id=r["id"], джерело="база НМТ", рік=r.get("рік"), тип=r.get("тип"),
                           умова=re.sub(r"(?<!\\)%[^\n]*", "", blocks[r["id"]]).strip(), відповідь=r.get("відповідь"),
                           категорія=r.get("категорія"), категорія_точна=True, теми=r.get("теми", []),
                           родини=sorted(S.родини(r)), складність=r.get("складність"), кроки=r.get("кроки"),
                           дефект=r.get("дефект"), поширення="так"))

    # 2. офіційні ЗНО (перенабір)
    for p in sorted(glob.glob(os.path.join(ЛОКАЛЬНЕ, "зно_офіційні", "завдання", "*.json"))):
        for t in завантажити(p, []):
            зразки.append(dict(id=t["id"], джерело="ЗНО офіційні", рік=t["рік"], сесія=t["сесія"], номер=t["номер"],
                               тип=t["тип"], умова=t["latex"], відповідь=t["ключ"], категорія=None, категорія_точна=False,
                               тема=t.get("тема"), розвʼязок=t.get("розвʼязок"), поширення="так"))

    # 3. osvita (без тих, що вже є в базі НМТ)
    for r in завантажити(os.path.join(ЛОКАЛЬНЕ, "osvita", "завдання.json"), []):
        if r.get("є_в_базі"): пропущено["osvita: уже в базі НМТ"] += 1; continue
        зразки.append(dict(id=r["id"], джерело="osvita", рік=r["рік"], іспит=r["іспит"], сесія=r["сесія"], номер=r["номер"],
                           тип=r["тип"], умова=r["умова"], варіанти=r.get("варіанти"), заголовки=r.get("заголовки"),
                           пункти=r.get("пункти"), відповідь=r.get("відповідь"), категорія=r.get("орієнтовна_категорія"),
                           категорія_точна=False, теми=r.get("теми", []), родини=r.get("родини", []),
                           рисунки=[os.path.join("локальне", "osvita", f) for f in r.get("рисунки", [])],
                           поширення="ні", посилання=r.get("джерело")))
    osv_ids = {z["id"] for z in зразки if z["джерело"] == "osvita"}

    # 4. ClassTime: одна картинка на групу дублікатів; що є в базі -- пропускаємо, що є в osvita -- картинку дописуємо туди
    ct = завантажити(os.path.join(ЛОКАЛЬНЕ, "classtime", "каталог.json"), [])
    за_id = {z["id"]: z for z in зразки}
    groups = collections.defaultdict(list)
    for r in ct: groups[r.get("кластер") or r["id"]].append(r)
    for g in groups.values():
        g.sort(key=lambda r: (r.get("відповідь") is None, -r.get("вживань", 0)))   # з відповіддю й найуживаніша -- першою
        r = g[0]
        if any(x.get("є_в_базі") for x in g): пропущено["ClassTime: уже в базі НМТ"] += 1; continue
        osv = next((x["є_в_osvita"] for x in g if x.get("є_в_osvita") in osv_ids), None)
        if osv:
            за_id[osv].setdefault("картинки_classtime", []).append(r["картинка"])
            if not за_id[osv].get("відповідь") and r.get("відповідь"): за_id[osv]["відповідь"] = r["відповідь"]
            пропущено["ClassTime: є в osvita (картинку дописано)"] += 1; continue
        зразки.append(dict(id=r["id"], джерело="ClassTime", тип=r.get("тип"), умова=r.get("текст", ""), умова_з_картинки=True,
                           картинка=r.get("картинка"), відповідь=r.get("відповідь"), категорія=r.get("орієнтовна_категорія"),
                           категорія_точна=False, теми=r.get("теми", []), родини=r.get("родини", []),
                           набори=r.get("набори"), теки=r.get("теки"), дублікатів=len(g), поширення=r.get("поширення", "так")))

    json.dump(зразки, open(ВИХІД, "w", encoding="utf-8"), ensure_ascii=False, indent=0)

    # підсумок
    дж = collections.Counter(z["джерело"] for z in зразки)
    print("зразків: %d  (%s)" % (len(зразки), ", ".join("%s %d" % kv for kv in дж.most_common())))
    for k, n in пропущено.items(): print("  пропущено/злито -- %s: %d" % (k, n))
    print("з відповіддю: %d; з картинкою чи рисунком: %d" % (
        sum(1 for z in зразки if z.get("відповідь")), sum(1 for z in зразки if z.get("картинка") or z.get("рисунки"))))
    print("\nслот                          усього   база  osvita  ClassTime")
    per = collections.defaultdict(collections.Counter)
    for z in зразки: per[z.get("категорія") or "без категорії"][z["джерело"]] += 1
    for c in list(S.СТРУКТУРА_2026) + sorted(set(per) - set(S.СТРУКТУРА_2026)):
        if c not in per: continue
        n = per[c]
        print("%-28s %6d %6d %7d %9d" % (c, sum(n.values()), n["база НМТ"], n["osvita"], n["ClassTime"]))
    print("\nзаписано", os.path.relpath(ВИХІД, ROOT))


if __name__ == "__main__":
    main()
