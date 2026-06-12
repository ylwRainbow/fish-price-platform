import argparse
import schedule
import time
import logging
from datetime import datetime, timedelta
from . import data_loader as dl
from . import repository as repo
from . import connectors as conn

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def ingest_wechat_sources(start: str = None, end: str = None):
    cfg = dl.CFG
    repo.ensure_catalog(cfg["fishes"], cfg["markets"])
    wechat_sources = [s for s in cfg["sources"] if s.get("type") == "wechat_mp"]
    if not wechat_sources:
        logger.warning("No wechat_mp sources found in config")
        return
    logger.info(f"Found {len(wechat_sources)} wechat_mp sources")
    for src in wechat_sources:
        fish = next((f for f in cfg["fishes"] if f["code"] == src["fish_code"]), None)
        market = next((m for m in cfg["markets"] if m["code"] == src["market_code"]), None)
        if not fish or not market:
            logger.warning(f"Skipping source: fish or market not found for {src}")
            continue
        logger.info(f"Fetching from WeChat: {src['params'].get('account_name')} for {fish['name']}")
        try:
            c = conn.connector_from_source(src)
            pts = c.fetch(fish, market, start or "", end or "")
            if pts:
                logger.info(f"Found {len(pts)} price points for {fish['name']}")
                repo.insert_prices(fish["id"], market["id"], pts, price_type="wechat", source_url=None)
            else:
                logger.warning(f"No price points found for {fish['name']}")
        except Exception as e:
            logger.error(f"Error fetching {fish['name']}: {e}")

def job():
    logger.info("Starting weekly WeChat ingestion job")
    today = datetime.now().date()
    start = (today - timedelta(days=7)).isoformat()
    end = today.isoformat()
    ingest_wechat_sources(start, end)
    logger.info("Weekly WeChat ingestion job completed")

def run_scheduler():
    logger.info("Starting WeChat ingestion scheduler - runs every Monday at 8:00 AM")
    schedule.every().monday.at("08:00").do(job)
    while True:
        schedule.run_pending()
        time.sleep(60)

def main():
    parser = argparse.ArgumentParser(description="WeChat MP price ingestion")
    parser.add_argument("--start", type=str, help="Start date (YYYY-MM-DD)")
    parser.add_argument("--end", type=str, help="End date (YYYY-MM-DD)")
    parser.add_argument("--schedule", action="store_true", help="Run as scheduled job (weekly)")
    args = parser.parse_args()
    if args.schedule:
        run_scheduler()
    else:
        if not args.start or not args.end:
            today = datetime.now().date()
            args.start = (today - timedelta(days=7)).isoformat()
            args.end = today.isoformat()
        logger.info(f"Running one-time ingestion from {args.start} to {args.end}")
        ingest_wechat_sources(args.start, args.end)
        logger.info("Ingestion completed")

if __name__ == "__main__":
    main()
