"""
EG_toppers Universe Updater
---------------------------
Haalt alle aandelen, fundamentele cijfers en koershistorie op uit de
EasyGrowth Cloud API en berekent voor elk aandeel de 1J/3J/5J/10J
log-lineaire regressie (Koersgroei/jr & Trendkwaliteit R²).

Wordt automatisch elke weekdag om middernacht uitgevoerd via GitHub Actions
(.github/workflows/update-universe.yml), en kan ook lokaal gedraaid worden:
    python update_universe.py
"""

from datetime import datetime, timezone, timedelta
import json
import math
import urllib.parse
import urllib.request
from concurrent.futures import ThreadPoolExecutor, as_completed

BASE_API_URL = "https://www.easygrowth.org/api"
OUTPUT_FILE = "eg_live_universe.js"
MIN_EXPECTED_STOCKS = 500


def fetch_json(endpoint: str):
    url = f"{BASE_API_URL}{endpoint}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=30) as resp:
        return json.loads(resp.read().decode("utf-8"))


def calc_log_reg_metrics(prices: list[float], days: int):
    if not prices or len(prices) < int(days * 0.85):
        return None
    slice_p = prices[-days:]
    n = len(slice_p)
    if n < 20 or any(p <= 0 for p in slice_p):
        return None

    log_p = [math.log(p) for p in slice_p]
    t = [i / (n - 1) for i in range(n)]

    sum_t = sum(t)
    sum_y = sum(log_p)
    mean_y = sum_y / n
    sum_ty = sum(t[i] * log_p[i] for i in range(n))
    sum_tt = sum(x * x for x in t)

    denom = n * sum_tt - sum_t * sum_t
    if denom == 0:
        return None

    slope = (n * sum_ty - sum_t * sum_y) / denom
    intercept = (sum_y - slope * sum_t) / n

    ss_tot = sum((y - mean_y) ** 2 for y in log_p)
    ss_res = sum((log_p[i] - (intercept + slope * t[i])) ** 2 for i in range(n))
    r2 = max(0.0, 1.0 - (ss_res / ss_tot)) if ss_tot > 0 else 0.0
    r = math.sqrt(r2)

    years = days / 252.0
    ret_tot = (slice_p[-1] - slice_p[0]) / slice_p[0]
    ret_ann = ((1.0 + max(-0.99, ret_tot)) ** (1.0 / years) - 1.0) * 100.0

    tk_r = round(r * 100.0, 1) if slope > 0 else 0.0
    tk_r2 = round(r2 * 100.0, 1) if slope > 0 else 0.0

    return {
        "ret": round(ret_ann, 1),
        "tk_r": tk_r,
        "tk_r2": tk_r2,
    }


def fetch_quotes_for_symbol(symbol: str) -> tuple[str, list[float]]:
    try:
        raw = fetch_json(f"/stockquotes?symbol={urllib.parse.quote(symbol)}")
        if raw and isinstance(raw, list):
            prices = [float(row[4]) for row in raw if len(row) > 4 and row[4] is not None]
            return symbol, prices
    except Exception:
        pass
    return symbol, []


def main():
    print(f"1. Aandelensymbolen ophalen van {BASE_API_URL}/searchStocks ...")
    raw_stocks = fetch_json("/searchStocks") or []
    symbols = [
        (s.get("Company") or s.get("symbol") or "").strip().upper()
        for s in raw_stocks
        if s.get("Company") or s.get("symbol")
    ]
    print(f"   {len(symbols)} symbolen gevonden.")

    if len(symbols) < MIN_EXPECTED_STOCKS:
        raise RuntimeError(
            f"Te weinig symbolen ontvangen van API ({len(symbols)} < {MIN_EXPECTED_STOCKS}). Update afgebroken om bestaande data te beschermen."
        )

    print("2. Fundamentele bedrijfsdata ophalen in batches van 150 ...")
    chunk_size = 150
    universe = []
    for i in range(0, len(symbols), chunk_size):
        chunk = symbols[i : i + chunk_size]
        encoded = urllib.parse.quote(",".join(chunk))
        rows = fetch_json(f"/readstocks?user_name=ivo&stocklist={encoded}") or []
        for d in rows:
            sym = (d.get("Company") or d.get("Symbol") or "").strip().upper()
            if not sym:
                continue
            universe.append(
                {
                    "Symbol": sym,
                    "Name": d.get("Name") or sym,
                    "Industry": d.get("Industry") or "N/A",
                    "Sector": d.get("Sector") or "N/A",
                    "Price": float(d.get("Value") or d.get("FairValue") or d.get("HoogstePrijs") or 0),
                    "ROIC": float(d.get("AvgRoic5y") or 0),
                    "EPSGrowth": max(float(d.get("LTEpsGrowth") or 0), float(d.get("WpaGroei") or 0)),
                    "RevGrowth": max(float(d.get("RevGrowth5y") or 0), float(d.get("OmzetGroei") or 0)),
                    "NetProfitMargin": float(d.get("NetProfitMargin") or 0),
                    "Perf1Y": float(d.get("Perf1Y") or 0),
                    "Perf3Y": float(d.get("Perf3Y") or 0),
                    "Perf5Y": float(d.get("Perf5Y") or 0),
                    "DebtEquity": float(d.get("DebtEquityRatio") or 0),
                    "CurrentRatio": float(d.get("CurrentRatio") or 0),
                    "FairValue": float(d.get("FairValue") or 0),
                    "Rating": float(d.get("Rating") or 50),
                }
            )

    if len(universe) < MIN_EXPECTED_STOCKS:
        raise RuntimeError(
            f"Te weinig fundamentele records ontvangen ({len(universe)} < {MIN_EXPECTED_STOCKS}). Update afgebroken."
        )

    universe.sort(key=lambda x: x["ROIC"], reverse=True)
    print(f"   {len(universe)} aandelen geladen.")

    all_symbols = [item["Symbol"] for item in universe]
    print(f"3. Koershistorie ophalen & regressie (R² / TK) berekenen voor alle {len(all_symbols)} aandelen ...")

    quotes_map: dict[str, list[float]] = {}
    completed = 0
    with ThreadPoolExecutor(max_workers=16) as pool:
        futures = {pool.submit(fetch_quotes_for_symbol, sym): sym for sym in all_symbols}
        for fut in as_completed(futures):
            sym, prices = fut.result()
            if prices:
                quotes_map[sym] = prices
            completed += 1
            if completed % 250 == 0 or completed == len(all_symbols):
                print(f"   Verwerkt: {completed} / {len(all_symbols)}")

    for item in universe:
        sym = item["Symbol"]
        prices = quotes_map.get(sym)
        if not prices:
            continue
        item["QuotesCount"] = len(prices)
        for days, suffix in ((2520, "10"), (1260, "5"), (756, "3"), (252, "1")):
            m = calc_log_reg_metrics(prices, days)
            if m:
                item[f"TK{suffix}"] = m["tk_r"]
                item[f"TK{suffix}_r2"] = m["tk_r2"]
                item[f"Ret{suffix}"] = m["ret"]

    cet_now = datetime.now(timezone(timedelta(hours=1)))
    updated_str = cet_now.strftime("%d-%m-%Y")

    print(f"4. Opslaan naar {OUTPUT_FILE} (datum: {updated_str}) ...")
    with open(OUTPUT_FILE, "w", encoding="utf-8") as f:
        f.write("/* Live EasyGrowth Universe Cached Dataset */\n")
        f.write(f'window.egLastUpdated = "{updated_str}";\n')
        f.write("window.egLiveUniverse = " + json.dumps(universe) + ";\n")

    print("Voltooid! Dataset succesvol bijgewerkt.")


if __name__ == "__main__":
    main()
