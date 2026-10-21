"""오피넷 국제 석유제품(싱가포르) 나프타 시세를 data/naphtha.json 으로 저장.

GitHub Actions 에서 주기적으로 실행된다. 값이 바뀌지 않았으면 파일을 건드리지 않는다.
"""
import json
import re
import sys
from datetime import date, datetime, timedelta, timezone
from pathlib import Path

import requests

OPINET_URL = "https://www.opinet.co.kr/glopopdSelect.do"
NAPHTHA_CODE = "F001"
YEARS_BACK = 3
CHUNK_DAYS = 365          # 요청 1건당 최대 조회 기간 (기간 분할)
KST = timezone(timedelta(hours=9))
OUT = Path(__file__).resolve().parent.parent / "data" / "naphtha.json"

ROW_RE = re.compile(
    r'<td class="nobd_l"\s*>\s*(\d{2})년(\d{2})월(\d{2})일\s*</td>\s*'
    r'<td[^>]*>\s*([^<]*?)\s*</td>'
)


def _parse_tbody(html, tbody_id):
    """tbody 하나에서 {date: value} 추출. 휴장일('-')은 제외."""
    m = re.search(rf'<tbody id="{tbody_id}"[^>]*>(.*?)</tbody>', html, re.S)
    if not m:
        raise ValueError(f"응답에서 {tbody_id}를 찾지 못했습니다 (페이지 구조 변경 가능성)")
    out = {}
    for yy, mm, dd, val in ROW_RE.findall(m.group(1)):
        val = val.replace(",", "")
        if val in ("", "-"):
            continue
        out[f"20{yy}-{mm}-{dd}"] = float(val)
    return out


def _fetch_range(start, end):
    """오피넷 조회 폼과 동일한 POST 요청. 응답 한 번에 원/L(tbody1)와 $/Bbl(tbody2)가 모두 들어있다."""
    form = {
        "TERM": "D",
        "HOLIDAY_YN": "N",          # 휴일 제외
        "STA_Y": f"{start.year}", "STA_M": f"{start.month:02d}", "STA_D": f"{start.day:02d}",
        "END_Y": f"{end.year}", "END_M": f"{end.month:02d}", "END_D": f"{end.day:02d}",
        "OILSRTCD7": NAPHTHA_CODE,
        "OILSRTCD": NAPHTHA_CODE,
    }
    resp = requests.post(OPINET_URL, data=form, timeout=60,
                         headers={"User-Agent": "Mozilla/5.0", "Referer": OPINET_URL})
    resp.raise_for_status()
    resp.encoding = "utf-8"
    return _parse_tbody(resp.text, "tbody1"), _parse_tbody(resp.text, "tbody2")


def fetch_naphtha():
    end = datetime.now(KST).date()
    start = end.replace(year=end.year - YEARS_BACK) - timedelta(days=7)
    krw, usd = {}, {}
    cur = start
    while cur <= end:
        chunk_end = min(cur + timedelta(days=CHUNK_DAYS - 1), end)
        k, u = _fetch_range(cur, chunk_end)
        krw.update(k)
        usd.update(u)
        cur = chunk_end + timedelta(days=1)
    days = sorted(set(krw) & set(usd))
    return [{"date": d, "usd_bbl": usd[d], "krw_l": krw[d]} for d in days]


def main():
    rows = fetch_naphtha()
    if len(rows) < 100:
        sys.exit(f"데이터가 너무 적습니다({len(rows)}건). 오피넷 응답을 확인하세요.")

    if OUT.exists():
        old = json.loads(OUT.read_text(encoding="utf-8"))
        if old.get("data") == rows:
            print(f"변경 없음 (최신 {rows[-1]['date']})")
            return

    OUT.parent.mkdir(parents=True, exist_ok=True)
    doc = {
        "source": "한국석유공사 오피넷",
        "updated_at": datetime.now(KST).isoformat(timespec="seconds"),
        "data": rows,
    }
    OUT.write_text(json.dumps(doc, ensure_ascii=False, separators=(",", ":")), encoding="utf-8")
    print(f"저장: {len(rows)}건, {rows[0]['date']} ~ {rows[-1]['date']}, 최신 {rows[-1]}")


if __name__ == "__main__":
    main()
