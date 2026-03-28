#!/usr/bin/env python3
"""
🦅 RAPTOR GEOGRAFIA v2 — fix yfinance MultiIndex + ticker symbols
"""

import json, os
from datetime import datetime, date
import pytz
import yfinance as yf
import pandas as pd

ROME_TZ = pytz.timezone("Europe/Rome")

PAESI = {
    "IUSS.L":   "iShares MSCI Saudi Arabia UCITS ETF",
    "IBZL.L":   "iShares MSCI Brazil UCITS ETF",
    "XCHA.DE":  "Xtrackers CSI300 Swap UCITS ETF",
    "LCCN.PA":  "Amundi MSCI China UCITS ETF",
    "MCHN.DE":  "Invesco MSCI China All Shares UCITS ETF",
    "XCS3.DE":  "Xtrackers MSCI Malaysia UCITS ETF",
    "D5BI.DE":  "Xtrackers MSCI Mexico UCITS ETF",
    "FLXT.L":   "Franklin FTSE Taiwan UCITS ETF",
    "TURL.MI":  "Amundi MSCI Turkey UCITS ETF",
    "XCS4.DE":  "Xtrackers MSCI Thailand UCITS ETF",
    "SPXE.L":   "State Street SPDR S&P 500 EUR Acc H",
    "WS5X.MI":  "WisdomTree EURO STOXX 50",
    "XSMI.SW":  "Xtrackers Switzerland UCITS ETF",
    "VUKE.L":   "Vanguard FTSE 100 UCITS ETF",
    "VUKG.L":   "Vanguard FTSE 100 UCITS ETF GBP Acc",
    "HSTE.L":   "HSBC Hang Seng Tech UCITS ETF",
    "SP1E.L":   "L&G S&P 100 Equal Weight UCITS ETF",
    "LGUS.L":   "L&G US Equity UCITS ETF",
    "SPY5.L":   "State Street SPDR S&P 500 UCITS ETF",
    "VUSA.L":   "Vanguard S&P 500 UCITS ETF",
    "DJE.PA":   "Amundi Dow Jones Industrial Average UCITS ETF",
    "SAUS.L":   "iShares MSCI Australia UCITS ETF USD Acc",
    "FLXU.L":   "Franklin U.S. Equity UCITS ETF",
    "SPXJ.L":   "iShares MSCI Pacific ex-Japan UCITS ETF",
    "IS3U.DE":  "iShares MSCI France UCITS ETF",
    "XESD.DE":  "Xtrackers Spain UCITS ETF",
    "EXS1.DE":  "iShares Core DAX UCITS ETF",
    "INDO.PA":  "Amundi MSCI Indonesia UCITS ETF",
    "C40.PA":   "Amundi CAC 40 ESG UCITS ETF",
    "ITBL.MI":  "WisdomTree FTSE MIB Banks",
    "FLXI.L":   "Franklin FTSE India UCITS ETF",
    "XFVT.DE":  "Xtrackers Vietnam Swap UCITS ETF",
    "SRSA.L":   "iShares MSCI South Africa UCITS ETF",
    "CSNDX.SW": "iShares NASDAQ 100 UCITS ETF",
    "WNAS.MI":  "WisdomTree NASDAQ-100 ETP",
    "IAEX.AS":  "iShares AEX UCITS ETF",
    "IMIB.MI":  "iShares FTSE MIB UCITS ETF",
    "WMIB.MI":  "WisdomTree FTSE MIB",
    "CN1.PA":   "Amundi MSCI Nordic UCITS ETF",
    "FMI.MI":   "Amundi Italy MIB ESG UCITS ETF",
    "CSMIB.MI": "iShares FTSE MIB ETF EUR Acc",
    "IBCJ.DE":  "iShares MSCI Poland UCITS ETF",
    "XBAS.DE":  "Xtrackers MSCI Singapore UCITS ETF",
    "XPQP.DE":  "Xtrackers MSCI Philippines UCITS ETF",
    "KOR.MI":   "Amundi MSCI Korea UCITS ETF",
    "NORW.DE":  "Global X MSCI Norway UCITS ETF",
}

NEW_AREA = {
    "TAM.L":    "iShares MSCI EM Latin America UCITS ETF",
    "ALAT.PA":  "Amundi MSCI EM Latin America UCITS ETF",
    "CSCA.L":   "iShares MSCI Canada ETF USD Acc",
    "IQQ9.DE":  "iShares BIC 50 UCITS ETF",
    "IAPD.L":   "iShares Asia Pacific Dividend UCITS ETF",
    "IQQF.DE":  "iShares MSCI AC Far East ex-Japan UCITS ETF",
    "ISAC.L":   "iShares MSCI ACWI UCITS ETF",
    "SXRU.DE":  "iShares Dow Jones Industrial Avg ETF USD Acc",
    "SJPA.L":   "iShares Core MSCI Japan IMI UCITS ETF",
    "MEUD.PA":  "Amundi Core Stoxx Europe 600 UCITS ETF",
    "IUSE.L":   "iShares S&P 500 EUR Hedged UCITS ETF",
    "IJPE.L":   "iShares MSCI Japan EUR Hedged UCITS ETF",
    "IWDE.L":   "iShares MSCI World EUR Hedged UCITS ETF",
    "SEMA.L":   "iShares MSCI EM UCITS ETF USD Acc",
    "NQSE.DE":  "iShares NASDAQ 100 UCITS ETF",
    "XDEE.DE":  "Xtrackers S&P 500 Equal Weight EUR Hedged",
    "ESTR.PA":  "Amundi MSCI Eastern Europe Ex Russia UCITS ETF",
    "PAFR.PA":  "Amundi Pan Africa UCITS ETF",
    "CSEMAS.DE":"iShares MSCI EM Asia ETF USD Acc",
}

XEON_TICKER = "XEON.DE"

def get_ohlcv(ticker: str):
    """Download OHLCV and return plain float lists, handling MultiIndex columns."""
    try:
        df = yf.download(ticker, period="1y", interval="1d",
                         progress=False, auto_adjust=True)
    except Exception as e:
        print(f"download error: {e}")
        return None

    if df is None or df.empty:
        return None

    # Fix MultiIndex columns (yfinance >= 0.2.x returns ('Close','TICKER'))
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)

    df = df.loc[:, ~df.columns.duplicated()]
    df = df.dropna(subset=['Close', 'High', 'Low'])

    if len(df) < 55:
        return None

    return {
        'close': [float(x) for x in df['Close'].tolist()],
        'high':  [float(x) for x in df['High'].tolist()],
        'low':   [float(x) for x in df['Low'].tolist()],
    }

def ema(values, period):
    k = 2 / (period + 1)
    r = [values[0]]
    for v in values[1:]:
        r.append(v * k + r[-1] * (1 - k))
    return r

def kama(prices, n=10, fast=2, slow=30):
    fsc = 2/(fast+1); ssc = 2/(slow+1)
    result = list(prices[:n])
    for i in range(n, len(prices)):
        d = abs(prices[i] - prices[i-n])
        v = sum(abs(prices[j]-prices[j-1]) for j in range(i-n+1, i+1))
        er = d/v if v > 0 else 0
        sc = (er*(fsc-ssc)+ssc)**2
        result.append(result[-1] + sc*(prices[i]-result[-1]))
    return result

def calc_er(p, n=10):
    if len(p) < n+1: return 0.0
    d = abs(p[-1]-p[-n-1])
    v = sum(abs(p[i]-p[i-1]) for i in range(-n,0))
    return round(d/v if v > 0 else 0, 4)

def calc_ao_baffetti(high, low):
    mid = [(h+l)/2 for h,l in zip(high,low)]
    if len(mid) < 34: return 0.0, 0
    series = [sum(mid[i-4:i+1])/5 - sum(mid[i-33:i+1])/34 for i in range(33,len(mid))]
    baff = 0
    for i in range(len(series)-1, 0, -1):
        if series[i] > series[i-1]: baff += 1
        else: break
    return round(series[-1], 6), baff

def calc_rsi(p, n=14):
    if len(p) < n+1: return 50.0
    d = [p[i]-p[i-1] for i in range(1,len(p))]
    g = [max(x,0) for x in d]; l = [max(-x,0) for x in d]
    ag = sum(g[:n])/n; al = sum(l[:n])/n
    for i in range(n,len(g)):
        ag=(ag*(n-1)+g[i])/n; al=(al*(n-1)+l[i])/n
    rs = ag/al if al>0 else 100
    return round(100-100/(1+rs),1)

def calc_atr(high, low, close, n=14):
    if len(close)<2: return 0.0
    tr=[max(high[i]-low[i],abs(high[i]-close[i-1]),abs(low[i]-close[i-1])) for i in range(1,len(close))]
    av=sum(tr[:n])/min(n,len(tr))
    for i in range(min(n,len(tr)),len(tr)): av=(av*(n-1)+tr[i])/n
    return round(av,5)

def calc_sar(high, low, af0=0.02, af_max=0.2):
    if len(high)<5: return float(low[-1]), True
    sar=low[0]; ep=high[0]; af=af0; bull=True; sars=[sar]
    for i in range(1,len(high)):
        prev=sars[-1]
        if bull:
            new=prev+af*(ep-prev)
            new=min(new, low[max(0,i-1)], low[max(0,i-2)])
            if low[i]<new: bull=False; new=ep; ep=low[i]; af=af0
            else:
                if high[i]>ep: ep=high[i]; af=min(af+af0,af_max)
        else:
            new=prev+af*(ep-prev)
            new=max(new, high[max(0,i-1)], high[max(0,i-2)])
            if high[i]>new: bull=True; new=ep; ep=high[i]; af=af0
            else:
                if low[i]<ep: ep=low[i]; af=min(af+af0,af_max)
        sars.append(new)
    return round(sars[-1],5), bull

def calc_supertrend(high, low, close, period=10, mult=3.0):
    if len(close)<period+2: return float(close[-1]), True
    tr=[max(high[i]-low[i],abs(high[i]-close[i-1]),abs(low[i]-close[i-1])) for i in range(1,len(close))]
    atr_l=[sum(tr[:period])/period]
    for i in range(period,len(tr)): atr_l.append((atr_l[-1]*(period-1)+tr[i])/period)
    pad=len(close)-len(atr_l)-1
    atr_f=[atr_l[0]]*(pad+1)+atr_l
    hl2=[(high[i]+low[i])/2 for i in range(len(close))]
    upper=[hl2[i]+mult*atr_f[i] for i in range(len(close))]
    lower=[hl2[i]-mult*atr_f[i] for i in range(len(close))]
    st=[lower[0]]; dir_=[1]
    for i in range(1,len(close)):
        ps=st[-1]
        if close[i]>ps:
            ns=max(lower[i],ps) if dir_[-1]==1 else lower[i]; dir_.append(1)
        else:
            ns=min(upper[i],ps) if dir_[-1]==-1 else upper[i]; dir_.append(-1)
        st.append(ns)
    return round(st[-1],5), dir_[-1]==1

def trendycator_calc(close):
    if len(close)<55: return "GRIGIO"
    e21=ema(close,21); e55=ema(close,55)
    if close[-1]>e21[-1]>e55[-1]: return "VERDE"
    if close[-1]<e21[-1]<e55[-1]: return "ROSSO"
    return "GRIGIO"

def mm_align(close):
    if len(close)<200: return False
    return close[-1]>sum(close[-20:])/20>sum(close[-50:])/50>sum(close[-200:])/200

def calc_score(er,baff,k_pct,p7,p30,mm_ok,ao_pos,cross,trend):
    s=(er*30+min(baff,10)*5+min(abs(k_pct),5)*3
       +max(-10,min(5,p7))*4+max(-20,min(10,p30))*2
       +(10 if mm_ok else 0)+(5 if ao_pos else 0)
       +(20 if cross<=3 else 12 if cross<=10 else 5 if cross<=20 else 0))
    if trend=="ROSSO": s*=0.6
    return round(s,1)

def calc_signal(price,kama_v,er,baff,trend,ao,mm_ok):
    if price<kama_v and trend=="ROSSO": return "STOP"
    if price<kama_v: return "USCITA"
    if ao<=0 or trend=="GRIGIO": return "ATTENZIONE"
    if trend=="VERDE" and er>=0.50 and baff>=3 and mm_ok: return "LONG"
    if baff>=3 and trend in("VERDE","GRIGIO"): return "EARLY"
    if baff>=1 and trend in("VERDE","GRIGIO"): return "WATCH"
    return "ATTENZIONE"

def qualifies(signal,score,trend,er,baff,sar_bull,st_bull):
    return(signal in("LONG","EARLY","WATCH") and score>=40
           and trend=="VERDE" and er>=0.50 and baff>=3 and sar_bull and st_bull)

def analyze(ticker, name):
    try:
        ohlcv = get_ohlcv(ticker)
        if ohlcv is None: return None
        close=ohlcv['close']; high=ohlcv['high']; low=ohlcv['low']
        price=close[-1]
        kama_s=kama(close); kama_v=kama_s[-1]
        k_pct=round((price/kama_v-1)*100 if kama_v else 0,2)
        er=calc_er(close); ao,baff=calc_ao_baffetti(high,low)
        rsi_v=calc_rsi(close); atr_v=calc_atr(high,low,close)
        trail=round(price-2*atr_v,4)
        trend=trendycator_calc(close); mm_ok=mm_align(close)
        sar_v,sar_bull=calc_sar(high,low)
        st_v,st_bull=calc_supertrend(high,low,close)
        p7=round((price/close[-8]-1)*100 if len(close)>=8 else 0,2)
        p30=round((price/close[-31]-1)*100 if len(close)>=31 else 0,2)
        cross=0
        for i in range(len(kama_s)-1,0,-1):
            if(close[i]>kama_s[i])==(price>kama_v): cross+=1
            else: break
        score=calc_score(er,baff,k_pct,p7,p30,mm_ok,ao>0,cross,trend)
        signal=calc_signal(price,kama_v,er,baff,trend,ao,mm_ok)
        q=qualifies(signal,score,trend,er,baff,sar_bull,st_bull)
        return{"ticker":ticker,"name":name,"price":round(price,4),"kama":round(kama_v,4),
               "k_pct":k_pct,"er":er,"ao":round(float(ao),6),"baffetti":baff,"rsi":rsi_v,
               "atr":round(atr_v,5),"trailing_stop":trail,"trend":trend,"mm_aligned":mm_ok,
               "sar":sar_v,"sar_bullish":sar_bull,"supertrend":st_v,"supertrend_bullish":st_bull,
               "perf7":p7,"perf30":p30,"score":score,"signal":signal,"qualifies":q}
    except Exception as e:
        print(f"  ✗ {ticker}: {e}")
        return None

STATE_FILE="portfolio_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f: return json.load(f)
    return{"paesi":{"positions":[],"history":[]},"new_area":{"positions":[],"history":[]}}

def save_state(state):
    with open(STATE_FILE,"w") as f: json.dump(state,f,indent=2,default=str)

def update_portfolio(existing,candidates,today_str):
    today=date.fromisoformat(today_str); kept=[]; exited=[]
    for pos in existing:
        cur=next((c for c in candidates if c["ticker"]==pos["ticker"]),None)
        if cur is None: pos["warning"]="Dati non disponibili"; kept.append(pos); continue
        entry_date=date.fromisoformat(pos["entry_date"])
        days_held=(today-entry_date).days
        cur_gain=round((cur["price"]/pos["entry_price"]-1)*100,2)
        new_trail=round(cur["price"]-2*cur["atr"],4)
        trail_stop=max(pos.get("trailing_stop",new_trail),new_trail)
        exit_reason=None
        if cur["k_pct"]<0: exit_reason="K% negativo — prezzo sotto KAMA"
        elif cur["price"]<=trail_stop: exit_reason="Trailing Stop colpito"
        elif cur["score"]<20: exit_reason="Score < 20"
        elif days_held>=10: exit_reason=f"Time Stop — {days_held} giorni"
        if exit_reason:
            exited.append({**pos,"exit_reason":exit_reason,"exit_price":cur["price"],
                           "final_gain_pct":cur_gain,"exit_date":today_str})
            continue
        pos.update({"current_price":cur["price"],"current_gain_pct":cur_gain,
                    "days_held":days_held,"trailing_stop":trail_stop,
                    "pre_alert":days_held>=7 and cur_gain<5.0,"target_hit":cur_gain>=5.0,
                    "signal":cur["signal"],"score":cur["score"],"er":cur["er"],
                    "trend":cur["trend"],"supertrend_bullish":cur["supertrend_bullish"],
                    "sar_bullish":cur["sar_bullish"],"perf7":cur["perf7"],"perf30":cur["perf30"],"warning":None})
        kept.append(pos)
    slots=5-len(kept); existing_tickers={p["ticker"] for p in kept}
    new_q=sorted([c for c in candidates if c["qualifies"] and c["ticker"] not in existing_tickers],
                 key=lambda x:x["er"],reverse=True)
    for c in new_q[:slots]:
        ep=c["price"]; stop=round(max(ep-2*c["atr"],c["trailing_stop"]),4)
        kept.append({"ticker":c["ticker"],"name":c["name"],"entry_date":today_str,
                     "entry_price":ep,"current_price":ep,"target_price":round(ep*1.05,4),
                     "stop_loss":stop,"trailing_stop":stop,"current_gain_pct":0.0,"days_held":0,
                     "pre_alert":False,"target_hit":False,"score":c["score"],"er":c["er"],
                     "signal":c["signal"],"trend":c["trend"],"supertrend_bullish":c["supertrend_bullish"],
                     "sar_bullish":c["sar_bullish"],"perf7":c["perf7"],"perf30":c["perf30"],"weight_pct":0,"warning":None})
    total_score=sum(p["score"] for p in kept)
    for p in kept: p["weight_pct"]=round(p["score"]/total_score*100,1) if total_score else 0
    return kept,exited

def main():
    now=datetime.now(ROME_TZ); today_str=now.date().isoformat()
    print(f"🦅 RAPTOR GEOGRAFIA v2 — {now.strftime('%d/%m/%Y %H:%M')} CET")
    state=load_state()
    print("\n📊 PAESI...")
    paesi_data=[]
    for t,n in PAESI.items():
        print(f"  {t}...",end=" ",flush=True)
        r=analyze(t,n)
        if r: paesi_data.append(r); print(f"✓ score={r['score']} er={r['er']} signal={r['signal']}")
        else: print("✗")
    print("\n📊 NEW AREA...")
    new_area_data=[]
    for t,n in NEW_AREA.items():
        print(f"  {t}...",end=" ",flush=True)
        r=analyze(t,n)
        if r: new_area_data.append(r); print(f"✓ score={r['score']} er={r['er']} signal={r['signal']}")
        else: print("✗")
    print("\n💰 XEON...")
    xeon=analyze(XEON_TICKER,"Xtrackers EUR Overnight Rate Swap UCITS ETF")
    print(f"  {'✓ price='+str(xeon['price']) if xeon else '✗ non trovato'}")
    paesi_pos,paesi_exited=update_portfolio(state["paesi"].get("positions",[]),paesi_data,today_str)
    new_area_pos,new_area_exited=update_portfolio(state["new_area"].get("positions",[]),new_area_data,today_str)
    state["paesi"]["positions"]=paesi_pos; state["new_area"]["positions"]=new_area_pos
    state["paesi"].setdefault("history",[]).extend(paesi_exited)
    state["new_area"].setdefault("history",[]).extend(new_area_exited)
    save_state(state)
    def top10(data): return sorted(data,key=lambda x:x["score"],reverse=True)[:10]
    output={"updated_at":now.isoformat(),"updated_display":now.strftime("%d/%m/%Y %H:%M CET"),
            "paesi":{"positions":paesi_pos,"use_xeon":len(paesi_pos)==0,
                     "xeon_price":xeon["price"] if xeon else None,
                     "watchlist":top10([d for d in paesi_data if not d["qualifies"]]),
                     "qualified":[d for d in paesi_data if d["qualifies"]],
                     "all":sorted(paesi_data,key=lambda x:x["score"],reverse=True)},
            "new_area":{"positions":new_area_pos,"use_xeon":len(new_area_pos)==0,
                        "xeon_price":xeon["price"] if xeon else None,
                        "watchlist":top10([d for d in new_area_data if not d["qualifies"]]),
                        "qualified":[d for d in new_area_data if d["qualifies"]],
                        "all":sorted(new_area_data,key=lambda x:x["score"],reverse=True)},
            "xeon":xeon}
    with open("geografia.json","w") as f: json.dump(output,f,indent=2,default=str)
    print(f"\n✅ geografia.json aggiornato")
    print(f"   PAESI    : {len(paesi_data)} analizzati | {len(paesi_pos)} posizioni {'| XEON 100%' if not paesi_pos else ''}")
    print(f"   NEW AREA : {len(new_area_data)} analizzati | {len(new_area_pos)} posizioni {'| XEON 100%' if not new_area_pos else ''}")

if __name__=="__main__":
    main()
