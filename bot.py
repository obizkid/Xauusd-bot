import asyncio,logging
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
TELEGRAM_TOKEN="8963591912:AAH80HPPt0WG6O7BFt5E4D9nJaenCaj0kfk"
TELEGRAM_CHAT_ID="6985270264"
logging.basicConfig(level=logging.INFO)
log=logging.getLogger(__name__)
async def run():
 log.info("Sending message...")
 try:
  await Bot(TELEGRAM_TOKEN).send_message(TELEGRAM_CHAT_ID,"Bot is alive! XAU/USD signal bot is running.")
  log.info("Message sent!")
 except Exception as e:log.error(e)
async def main():
 s=AsyncIOScheduler(timezone="UTC");s.add_job(run,"cron",minute="*/15");s.start()
 await run()
 while True:await asyncio.sleep(60)
asyncio.run(main())
