import json
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
CFG = json.loads((ROOT / "config" / "metrics.json").read_text(encoding="utf-8"))

def num(v):
    if v is None: return None
    s = str(v).replace(",", "").strip()
    if s in ("", "-", "--"): return None
    try: return float(s)
    except ValueError: return None

def find(rows, aliases):
    for alias in aliases:
        for row in rows:
            name = row.get("account_nm", "").strip()
            if name == alias or alias in name:
                value = num(row.get("thstrm_amount"))
                if value is not None: return value
    return None

def main():
    records = []
    for path in sorted((ROOT / "data" / "raw").glob("*/*.json")):
        year = int(path.parent.name)
        period = path.stem.split("_")[0]
        if period not in CFG["reports"]: continue
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data.get("list", [])
        values = {k: find(rows, aliases) for k, aliases in CFG["metrics"].items()}
        rev, op, ni = values["revenue"], values["operating_profit"], values["net_income"]
        assets, liab, equity = values["total_assets"], values["total_liabilities"], values["total_equity"]
        ca, cl, cash = values["current_assets"], values["current_liabilities"], values["cash"]
        values["operating_margin"] = op / rev * 100 if op is not None and rev else None
        values["net_margin"] = ni / rev * 100 if ni is not None and rev else None
        values["roa"] = ni / assets * 100 if ni is not None and assets else None
        values["roe"] = ni / equity * 100 if ni is not None and equity else None
        values["debt_ratio"] = liab / equity * 100 if liab is not None and equity else None
        values["current_ratio"] = ca / cl * 100 if ca is not None and cl else None
        values["cash_ratio"] = cash / cl * 100 if cash is not None and cl else None
        values["rd_ratio"] = values["rd_expense"] / rev * 100 if values["rd_expense"] is not None and rev else None
        labels = {"annual": "Annual", "half_year": "H1", "q1": "Q1", "q3": "Q3"}
        records.append({"year": year, "period": period, "period_label": labels[period], "fs_div": data.get("fs_div"), **values})
    columns = ["year","period","period_label","fs_div"] + list(CFG["metrics"].keys()) + ["operating_margin","net_margin","roa","roe","debt_ratio","current_ratio","cash_ratio","rd_ratio"]
    df = pd.DataFrame(records, columns=columns).sort_values(["year","period"])
    out = ROOT / "dashboard" / "data"
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "metrics.csv", index=False, encoding="utf-8-sig")
    (out / "metrics.json").write_text(df.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
