import asyncio,logging,urllib.request,json
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
TELEGRAM_TOKEN="8963591912:AAH80HPPt0WG6O7BFt5E4D9nJaenCaj0kfk"
TELEGRAM_CHAT_ID="6985270264"
logging.basicConfig(level=logging.INFO)
log=logging.getLogger(__name__)
def fetch():
 url="https://api.metals.live/v1/spot"
 d=json.loads(urllib.request.urlopen(url,timeout=15).read())
 price=None
 for item in d:
  if"gold"in item:price=float(item["gold"]);break
 if not price:raise ValueError("No gold price")
 return price
async def run():
 log.info("Scanning...")
 try:
  price=fetch()
  msg=f"XAU/USD Live Price\nGold: ${price:.2f}\nBot is running OK!"
  await Bot(TELEGRAM_TOKEN).send_message(TELEGRAM_CHAT_ID,msg)
  log.info(f"Sent price {price}")
 except Exception as e:log.error(e)
async def main():
 s=AsyncIOScheduler(timezone="UTC");s.add_job(run,"cron",minute="*/15");s.start()
 await run()
 while True:await asyncio.sleep(60)
asyncio.run(main())
