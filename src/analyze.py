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

def norm_name(v):
    return "".join(str(v or "").split())

def find(rows, aliases, sj_div=None):
    aliases_norm = [norm_name(a) for a in aliases]
    candidates = [r for r in rows if sj_div is None or r.get("sj_div") == sj_div]
    for alias in aliases_norm:
        for row in candidates:
            if norm_name(row.get("account_nm")) == alias:
                value = num(row.get("thstrm_amount"))
                if value is not None: return value
    return None

def average(prev, current):
    return (prev + current) / 2 if prev is not None and current is not None else current

def main():
    records = []
    for path in sorted((ROOT / "data" / "raw").glob("*/*.json")):
        year = int(path.parent.name)
        period = path.stem.rsplit("_", 1)[0]
        if period not in CFG["reports"]: continue
        data = json.loads(path.read_text(encoding="utf-8"))
        rows = data.get("list", [])

        values = {}
        for key, aliases in CFG["metrics"].items():
            if key in {"revenue", "gross_profit", "operating_profit", "net_income", "eps"}:
                values[key] = find(rows, aliases, "CIS")
            elif key == "operating_cash_flow":
                values[key] = find(rows, aliases, "CF") or find(rows, aliases)
            else:
                values[key] = find(rows, aliases, "BS")

        rev, op, ni = values["revenue"], values["operating_profit"], values["net_income"]
        assets, liab, equity = values["total_assets"], values["total_liabilities"], values["total_equity"]
        ca, cl, cash = values["current_assets"], values["current_liabilities"], values["cash"]

        values["operating_margin"] = op / rev * 100 if op is not None and rev else None
        values["net_margin"] = ni / rev * 100 if ni is not None and rev else None
        values["debt_ratio"] = liab / equity * 100 if liab is not None and equity else None
        values["current_ratio"] = ca / cl * 100 if ca is not None and cl else None
        values["cash_ratio"] = cash / cl * 100 if cash is not None and cl else None
        values["rd_ratio"] = values["rd_expense"] / rev * 100 if values["rd_expense"] is not None and rev else None

        prev_assets = prev_equity = None
        if period == "annual":
            prev_path = ROOT / "data" / "raw" / str(year - 1) / path.name.replace(str(year), str(year - 1))
            if prev_path.exists():
                prev_rows = json.loads(prev_path.read_text(encoding="utf-8")).get("list", [])
                prev_assets = find(prev_rows, CFG["metrics"]["total_assets"], "BS")
                prev_equity = find(prev_rows, CFG["metrics"]["total_equity"], "BS")
        values["roa"] = ni / average(prev_assets, assets) * 100 if ni is not None and average(prev_assets, assets) else None
        values["roe"] = ni / average(prev_equity, equity) * 100 if ni is not None and average(prev_equity, equity) else None

        labels = {"annual": "Annual", "half_year": "H1", "q1": "Q1", "q3": "Q3"}
        records.append({"year": year, "period": period, "period_label": labels[period], "fs_div": data.get("fs_div"), **values})

    columns = ["year","period","period_label","fs_div"] + list(CFG["metrics"].keys()) + ["operating_margin","net_margin","roa","roe","debt_ratio","current_ratio","cash_ratio","rd_ratio"]
    df = pd.DataFrame(records, columns=columns)
    if df.empty:
        raise RuntimeError("No DART financial records were produced. Check data/raw and DART API collection.")
    df = df.sort_values(["year","period"])
    out = ROOT / "dashboard" / "data"
    out.mkdir(parents=True, exist_ok=True)
    df.to_csv(out / "metrics.csv", index=False, encoding="utf-8-sig")
    (out / "metrics.json").write_text(df.to_json(orient="records", force_ascii=False, indent=2), encoding="utf-8")

if __name__ == "__main__":
    main()
