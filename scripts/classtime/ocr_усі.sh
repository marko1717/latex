#!/bin/sh
# розпізнати текст на ще не оброблених картинках (4 паралельні процеси); результат дописується в ocr.jsonl
D=~/НМТ_локальне/classtime
[ -x "$D/ocr" ] || swiftc -O "$(dirname "$0")/ocr.swift" -o "$D/ocr"
touch "$D/ocr.jsonl"
python3 - "$D" <<'PY'
import json, os, sys
D=sys.argv[1]
done=set()
for ln in open(os.path.join(D,'ocr.jsonl'),encoding='utf-8'):
    try: done.add(json.loads(ln)['path'])
    except Exception: pass
todo=[os.path.join(D,'картинки',f) for f in sorted(os.listdir(os.path.join(D,'картинки'))) if os.path.join(D,'картинки',f) not in done]
for k in range(4):
    open('/tmp/ct_ocr_%d.txt'%k,'w').write('\n'.join(todo[k::4])+'\n')
print('до розпізнавання:', len(todo), flush=True)
PY
for k in 0 1 2 3; do "$D/ocr" /tmp/ct_ocr_$k.txt > /tmp/ct_ocr_$k.jsonl & done; wait
cat /tmp/ct_ocr_0.jsonl /tmp/ct_ocr_1.jsonl /tmp/ct_ocr_2.jsonl /tmp/ct_ocr_3.jsonl >> "$D/ocr.jsonl"
echo "розпізнано всього: $(wc -l < "$D/ocr.jsonl")"
