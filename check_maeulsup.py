"""
전통마을숲 API 데이터 확인 스크립트

사용법
  1) pip install requests
  2) 인증키를 환경변수로 설정 (코드에 직접 쓰지 않기)
       Windows PowerShell : $env:DATA_GO_KR_KEY="인증키"
       Mac / Linux        : export DATA_GO_KR_KEY="인증키"
  3) 아래 OPERATION_URL 을 활용명세(Swagger)에 나온 전체 요청 주소로 바꾸기
  4) python check_maeulsup.py
  5) 터미널에 출력된 내용을 복사해서 대화창에 붙여넣기
"""
import csv
import json
import os
import re
import statistics
import sys
import xml.etree.ElementTree as ET
from urllib.parse import unquote

import requests

# 활용명세에서 확인한 오퍼레이션 주소로 교체 (End Point 뒤에 /오퍼레이션명 이 붙음)
OPERATION_URL = "https://apis.data.go.kr/1400000/cultureInfoService/traVllgFrstOpenAPI"
NUM_OF_ROWS = 100
MAX_PAGES = 20  # 일일 트래픽(1,000건) 보호용 상한

# 원본 텍스트가 cp949 기준 254바이트에서 잘려서 제공됨 (Shapefile DBF 텍스트 필드 한도로 추정)
TEXT_FIELDS = ["histrexmnncont", "clturexmnncont"]
TRUNC_BYTES = 253  # 한글 2바이트라 253 또는 254에서 멈춤 → 253 이상이면 잘린 것으로 판단
SENTENCE_END = re.compile(r"[.!?](?!\d)")  # 뒤에 숫자가 오는 소수점(1.5)은 제외, "음.저수지" 같은 붙여쓰기는 포함

key = os.environ.get("DATA_GO_KR_KEY")
if not key:
    sys.exit("DATA_GO_KR_KEY 환경변수가 없습니다. 사용법 2)를 확인하세요.")
# Encoding 키(%2F, %3D 포함)를 넣어도 동작하도록 디코딩해서 사용.
# requests 가 다시 인코딩하므로, 인코딩된 키를 그대로 넣으면 이중 인코딩으로 인증 오류가 난다.
key = unquote(key)


def fetch(page):
    params = {"serviceKey": key, "pageNo": page, "numOfRows": NUM_OF_ROWS}
    r = requests.get(OPERATION_URL, params=params, timeout=30)
    return r.status_code, r.text


def is_truncated(text):
    return len(text.encode("cp949", errors="replace")) >= TRUNC_BYTES


def trim_to_sentence(text):
    ends = list(SENTENCE_END.finditer(text))
    return text[: ends[-1].end()] if ends else text  # 끝맺은 문장이 없으면 원문 유지


def parse(xml_text):
    root = ET.fromstring(xml_text)
    code = root.findtext(".//resultCode") or root.findtext(".//returnReasonCode")
    msg = root.findtext(".//resultMsg") or root.findtext(".//returnAuthMsg")
    total = root.findtext(".//totalCount")
    items = [{c.tag: (c.text or "").strip() for c in it} for it in root.iter("item")]
    return code, msg, total, items


all_items = []
for page in range(1, MAX_PAGES + 1):
    status, text = fetch(page)
    if page == 1:
        with open("first_response.xml", "w", encoding="utf-8") as f:
            f.write(text)
        print("=== 첫 응답 앞부분 (HTTP", status, ") ===")
        print(text[:800])
        print()
    try:
        code, msg, total, items = parse(text)
    except ET.ParseError:
        print("XML 파싱 실패. 응답 원문 앞부분:")
        print(text[:500])
        sys.exit(1)
    if page == 1:
        print(f"resultCode={code} resultMsg={msg} totalCount={total}\n")
    if not items:
        break
    all_items.extend(items)
    if total and len(all_items) >= int(total):
        break

if not all_items:
    sys.exit("받은 레코드가 없습니다. 위 응답 내용을 그대로 붙여넣어 주세요.")

# 원본 저장 (엑셀에서 한글이 깨지지 않도록 utf-8-sig)
fields = []
for it in all_items:
    for k in it:
        if k not in fields:
            fields.append(k)

# 잘림 표시(_truncated)와 마지막 완결 문장까지만 남긴 텍스트(_clean) 추가. 원본 필드는 그대로 둠
extra_fields = []
for fld in TEXT_FIELDS:
    if fld not in fields:
        continue
    extra_fields += [f"{fld}_truncated", f"{fld}_clean"]
    for it in all_items:
        v = it.get(fld, "").strip()
        cut = is_truncated(v)
        it[f"{fld}_truncated"] = cut
        it[f"{fld}_clean"] = trim_to_sentence(v) if cut else v

with open("maeulsup_raw.json", "w", encoding="utf-8") as f:
    json.dump(all_items, f, ensure_ascii=False, indent=2)
with open("maeulsup_raw.csv", "w", encoding="utf-8-sig", newline="") as f:
    w = csv.DictWriter(f, fieldnames=fields + extra_fields)
    w.writeheader()
    w.writerows(all_items)

n = len(all_items)
print(f"=== 레코드 수: {n} ===\n")
print(f"{'필드':<28}{'빈값%':>7}{'평균길이':>9}{'최대길이':>9}")
long_fields = []
for fld in fields:
    vals = [it.get(fld, "") for it in all_items]
    filled = [v for v in vals if v.strip()]
    empty_pct = (n - len(filled)) / n * 100
    avg = statistics.mean(len(v) for v in filled) if filled else 0
    mx = max((len(v) for v in filled), default=0)
    print(f"{fld:<28}{empty_pct:>7.1f}{avg:>9.1f}{mx:>9}")
    if avg >= 30:
        long_fields.append(fld)

print(f"\n=== 긴 텍스트 필드 (평균 30자 이상): {long_fields} ===")
story_len = [sum(len(it.get(f, "")) for f in long_fields) for it in all_items]
for th in (100, 200, 500):
    cnt = sum(1 for s in story_len if s >= th)
    print(f"긴 텍스트 합계 {th}자 이상 레코드: {cnt}건 ({cnt / n * 100:.1f}%)")

print(f"\n=== 잘린 텍스트 (cp949 {TRUNC_BYTES}바이트 이상) ===")
for fld in TEXT_FIELDS:
    if fld not in fields:
        continue
    filled = sum(1 for it in all_items if it.get(fld, "").strip())
    cut = [it for it in all_items if it[f"{fld}_truncated"]]
    no_sentence = sum(1 for it in cut if it[f"{fld}_clean"] == it[fld].strip())
    lost = sum(len(it[fld].strip()) - len(it[f"{fld}_clean"]) for it in cut)
    print(f"{fld}: {len(cut)}건 / 내용 있음 {filled}건 "
          f"(정리로 버린 글자 평균 {lost / len(cut) if cut else 0:.1f}자, 완결 문장이 없어 원문 유지 {no_sentence}건)")

print("\n=== 텍스트가 가장 풍부한 레코드 3건 ===")
top = sorted(range(n), key=lambda i: story_len[i], reverse=True)[:3]
for i in top:
    print("-" * 60)
    for fld in fields:
        v = all_items[i].get(fld, "")
        print(f"[{fld}] {v[:300]}{'...' if len(v) > 300 else ''}")

print("\n저장된 파일: first_response.xml, maeulsup_raw.json, maeulsup_raw.csv")
