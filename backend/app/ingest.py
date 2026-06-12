import argparse
from datetime import datetime, timedelta
from . import data_loader as dl
from . import repository as repo
from . import connectors as conn

def ingest(start:str, end:str):
    cfg = dl.CFG
    repo.ensure_catalog(cfg["fishes"], cfg["markets"])
    for src in cfg["sources"]:
        fish = next(f for f in cfg["fishes"] if f["code"] == src["fish_code"])
        market = next(m for m in cfg["markets"] if m["code"] == src["market_code"])
        c = conn.connector_from_source(src)
        pts = c.fetch(fish, market, start, end)
        repo.insert_prices(fish["id"], market["id"], pts, price_type="pond", source_url=None)

def default_range():
    today = datetime.now().date()
    start = (today - timedelta(days=90)).isoformat()
    end = today.isoformat()
    return start, end

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--start", type=str, default=None)
    parser.add_argument("--end", type=str, default=None)
    args = parser.parse_args()
    s,e = (args.start, args.end) if (args.start and args.end) else default_range()
    ingest(s,e)
    print("Ingest done:", s, "to", e)

if __name__ == "__main__":
    main()
