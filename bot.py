import asyncio,logging,urllib.request,json
from telegram import Bot
from apscheduler.schedulers.asyncio import AsyncIOScheduler
TELEGRAM_TOKEN="8963591912:AAH80HPPt0WG6O7BFt5E4D9nJaenCaj0kfk"
TELEGRAM_CHAT_ID="6985270264"
logging.basicConfig(level=logging.INFO)
log=logging.getLogger(__name__)
def fetch():
 url="https://www.alphavantage.co/query?function=FX_INTRADAY&from_symbol=XAU&to_symbol=USD&interval=15min&outputsize=compact&apikey=demo"
 d=json.loads(urllib.request.urlopen(url,timeout=15).read())
 k="Time Series FX (15min)"
 if k not in d:raise ValueError(str(d))
 rows=sorted(d[k].items())
 return[{"o":float(v["1. open"]),"h":float(v["2. high"]),"l":float(v["3. low"]),"c":float(v["4. close"])}for t,v in rows][-50:]
def atr(cs,p=14):
 trs=[max(cs[i]["h"]-cs[i]["l"],abs(cs[i]["h"]-cs[i-1]["c"]),abs(cs[i]["l"]-cs[i-1]["c"]))for i in range(1,len(cs))]
 return sum(trs[-p:])/p
def sig(cs):
 if len(cs)<32:return None
 a=atr(cs);pr=cs[-1]["c"];p=cs[-2];c=cs[-1]
 bl=0;br=0;pt=[]
 if p["c"]<p["o"] and c["c"]>c["o"] and c["o"]<=p["c"] and c["c"]>=p["o"]:bl+=1;pt.append("Bullish Engulfing")
 if p["c"]>p["o"] and c["c"]<c["o"] and c["o"]>=p["c"] and c["c"]<=p["o"]:br+=1;pt.append("Bearish Engulfing")
 bd=abs(c["c"]-c["o"]);rng=c["h"]-c["l"]
 if rng>0 and(min(c["o"],c["c"])-c["l"])>=0.6*rng and bd<=0.3*rng:bl+=1;pt.append("Bullish Pin Bar")
 if rng>0 and(c["h"]-max(c["o"],c["c"]))>=0.6*rng and bd<=0.3*rng:br+=1;pt.append("Bearish Pin Bar")
 lb=cs[-31:-1];sh=max(x["h"]for x in lb);sl=min(x["l"]for x in lb)
 if c["c"]>sh:bl+=1;pt.append("Bullish BOS")
 elif c["c"]<sl:br+=1;pt.append("Bearish BOS")
 sup=[x["l"]for x in cs[:-1]if pr*0.985<x["l"]<pr]
 res=[x["h"]for x in cs[:-1]if pr<x["h"]<pr*1.015]
 if sup:bl+=1;pt.append(f"Near Support:{sorted(sup,reverse=True)[0]:.2f}")
 if res:br+=1;pt.append(f"Near Resistance:{sorted(res)[0]:.2f}")
 if bl>=2 and bl>br:
  e=pr;s=round(e-a*1.5,2);tp=round(e+a*2.5,2)
  return{"d":"BUY","e":round(e,2),"s":s,"t":tp,"r":round(abs(tp-e)/abs(s-e),2),"st":bl,"pt":pt,"a":round(a,2)}
 if br>=2 and br>bl:
  e=pr;s=round(e+a*1.5,2);tp=round(e-a*2.5,2)
  return{"d":"SELL","e":round(e,2),"s":s,"t":tp,"r":round(abs(tp-e)/abs(s-e),2),"st":br,"pt":pt,"a":round(a,2)}
async def run():
 log.info("Scanning...")
 try:
  cs=fetch();s=sig(cs)
  if s:
   pl="\n".join(f"* {p}"for p in s["pt"])
   em="BUY" if s["d"]=="BUY" else "SELL"
   msg=f"{em} XAU/USD\nEntry:{s['e']}\nSL:{s['s']}\nTP:{s['t']}\nRR:1:{s['r']}\n{pl}\nStrength:{s['st']}/4"
   await Bot(TELEGRAM_TOKEN).send_message(TELEGRAM_CHAT_ID,msg)
   log.info(f"Sent {s['d']}")
  else:log.info("No signal")
 except Exception as e:log.error(e)
async def main():
 s=AsyncIOScheduler(timezone="UTC");s.add_job(run,"cron",minute="*/15");s.start()
 await run()
 while True:await asyncio.sleep(60)
asyncio.run(main())
