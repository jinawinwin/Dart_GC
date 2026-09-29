import json
import os
from pathlib import Path
from datetime import datetime
from dart_client import DartClient

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config" / "metrics.json").read_text(encoding="utf-8"))
CORP = CFG["company"]["corp_code"]

def get_statement(client, year, code):
    last = None
    for fs_div in ("CFS", "OFS"):
        try:
            return fs_div, client.get("fnlttSinglAcntAll", {
                "corp_code": CORP, "bsns_year": str(year),
                "reprt_code": code, "fs_div": fs_div
            })
        except Exception as e:
            last = e
    raise last

def main():
    client = DartClient()
    start = int(os.getenv("START_YEAR", "2010"))
    end = int(os.getenv("END_YEAR", str(datetime.now().year)))
    manifest = []
    for year in range(start, end + 1):
        if year < 2015:
            manifest.append({"year": year, "status": "not_available_in_opendart_structured_financial_api"})
            continue
        for period, code in CFG["reports"].items():
            try:
                fs_div, data = get_statement(client, year, code)
                path = ROOT / "data" / "raw" / str(year) / (period + "_" + fs_div + ".json")
                path.parent.mkdir(parents=True, exist_ok=True)
                path.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
                manifest.append({"year": year, "period": period, "fs_div": fs_div, "status": "ok"})
            except Exception as e:
                manifest.append({"year": year, "period": period, "status": "error", "error": str(e)})
    (ROOT / "data" / "collection_manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
