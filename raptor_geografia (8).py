#!/usr/bin/env python3
"""
🦅 RAPTOR GEOGRAFIA v6 — Signal-only, no portfolio state
Genera: geografia.json + data/charts/TICKER.json + data/signals/TICKER.json
"""

import json, os, math
from datetime import datetime
import pytz
import yfinance as yf
import pandas as pd

ROME_TZ     = pytz.timezone("Europe/Rome")
OUTPUT_FILE = "geografia.json"
BENCHMARK   = "SWRD.MI"
XEON_TICKER = "XEON.MI"

PAESI = {
    "IUSS.MI":   "iShares MSCI Saudi Arabia UCITS ETF",
    "SAUDI.MI":  "Franklin FTSE Saudi Arabia UCITS ETF",
    "IBZL.MI":   "iShares MSCI Brazil UCITS ETF",
    "XCHA.DE":   "Xtrackers CSI300 Swap UCITS ETF",
    "LCCN.MI":   "Amundi MSCI China UCITS ETF",
    "WSPE.MI":   "WisdomTree S&P 500 EUR Daily Hedged",
    "MCHN.MI":   "Invesco MSCI China All Shares UCITS ETF",
    "XCS3.DE":   "Xtrackers MSCI Malaysia UCITS ETF",
    "D5BI.DE":   "Xtrackers MSCI Mexico UCITS ETF",
    "FLXT.MI":   "Franklin FTSE Taiwan UCITS ETF",
    "TUR.PA":    "Amundi MSCI Turkey UCITS ETF",
    "XCS4.DE":   "Xtrackers MSCI Thailand UCITS ETF",
    "WRD.PA":    "HSBC MSCI World UCITS ETF",
    "IBCJ.MI":   "iShares MSCI Poland UCITS ETF",
    "XBAS.DE":   "Xtrackers MSCI Singapore UCITS ETF",
    "IMIB.MI":   "iShares FTSE MIB UCITS ETF",
    "WMIB.MI":   "WisdomTree FTSE MIB",
    "CN1.PA":    "Amundi MSCI Nordic UCITS ETF",
    "FMI.MI":    "Amundi Italy MIB ESG UCITS ETF",
    "CSMIB.MI":  "iShares FTSE MIB ETF EUR Acc",
    "SPXE.MI":   "State Street SPDR S&P 500 EUR Acc Hedged",
    "UKE.MI":    "UBS MSCI United Kingdom hEUR Acc",
    "WS5X.MI":   "WisdomTree EURO STOXX 50",
    "XSMI.MI":   "Xtrackers Switzerland UCITS ETF",
    "HSTE.MI":   "HSBC Hang Seng Tech UCITS ETF",
    "SP1E.MI":   "L&G S&P 100 Equal Weight UCITS ETF",
    "WSPX.MI":   "WisdomTree S&P 500",
    "LGUS.MI":   "L&G US Equity UCITS ETF",
    "SPY5.MI":   "State Street SPDR S&P 500 UCITS ETF",
    "VUSA.MI":   "Vanguard S&P 500 UCITS ETF",
    "DJE.PA":    "Amundi Dow Jones Industrial Average UCITS ETF",
    "SAUS.MI":   "iShares MSCI Australia UCITS ETF EUR",
    "FLXU.MI":   "Franklin U.S. Equity UCITS ETF",
    "SPXJ.MI":   "iShares MSCI Pacific ex-Japan UCITS ETF",
    "IS3U.DE":   "iShares MSCI France UCITS ETF",
    "XESD.DE":   "Xtrackers Spain UCITS ETF",
    "EXS1.DE":   "iShares Core DAX UCITS ETF",
    "XDAX.DE":   "Xtrackers DAX UCITS ETF",
    "INDO.PA":   "Amundi MSCI Indonesia UCITS ETF",
    "C40.PA":    "Amundi CAC 40 ESG UCITS ETF",
    "ITBL.MI":   "WisdomTree FTSE MIB Banks",
    "XPQP.DE":   "Xtrackers MSCI Philippines UCITS ETF",
    "FLXI.MI":   "Franklin FTSE India UCITS ETF",
    "XFVT.DE":   "Xtrackers Vietnam Swap UCITS ETF",
    "AUHEUA.MI": "UBS MSCI Australia hEUR Acc",
    "VJPE.MI":   "Vanguard FTSE Japan EUR Hedged",
    "SRSA.MI":   "iShares MSCI South Africa UCITS ETF",
    "INDI.PA":   "Amundi MSCI India Swap UCITS ETF",
    "CSNDX.MI":  "iShares NASDAQ 100 UCITS ETF",
    "WNAS.MI":   "WisdomTree NASDAQ-100 ETP",
    "QTOP.MI":   "iShares Nasdaq 100 Top 30 UCITS ETF",
    "IAEX.AS":   "iShares AEX UCITS ETF",
    "XSFR.DE":   "Xtrackers S&P Select Frontier Swap UCITS ETF",
    "WRTY.MI":   "WisdomTree Russell 2000 ETP",
    "KOR.PA":    "Amundi MSCI Korea UCITS ETF",
    "GXDW.MI":   "Global X Dorsey Wright Thematic ETF",
    "NORW.MI":   "Global X MSCI Norway UCITS ETF",
    "LEER.DE":   "Xtrackers MSCI World Minimum Volatility UCITS ETF",
    "EST.MI":    "Amundi MSCI Eastern Europe Ex Russia UCITS ETF",
    "100H.MI":   "Amundi FTSE 100 EUR Hedged UCITS ETF",
    "SVE.MI":    "UBS MSCI Switzerland 20/35 UCITS ETF EUR",
}

NEW_AREA = {
    "ALAT.MI":   "Amundi MSCI EM Latin America UCITS ETF",
    "LTAM.MI":   "iShares MSCI EM Latin America UCITS ETF",
    "CSCA.MI":   "iShares MSCI Canada ETF EUR Acc",
    "IQQ9.DE":   "iShares BIC 50 UCITS ETF",
    "IAPD.MI":   "iShares Asia Pacific Dividend UCITS ETF",
    "CAHEUA.MI": "UBS MSCI Canada UCITS ETF hEUR Acc",
    "IQQF.DE":   "iShares MSCI AC Far East ex-Japan UCITS ETF",
    "CSPXJ.MI":  "iShares Core MSCI Pac ex-Jpn ETF EUR Acc",
    "ISAC.MI":   "iShares MSCI ACWI UCITS ETF",
    "SXRU.DE":   "iShares Dow Jones Industrial Avg ETF EUR Acc",
    "SJPA.MI":   "iShares Core MSCI Japan IMI UCITS ETF",
    "MEUD.PA":   "Amundi Core Stoxx Europe 600 UCITS ETF",
    "IUSE.MI":   "iShares S&P 500 EUR Hedged UCITS ETF",
    "IJPE.MI":   "iShares MSCI Japan EUR Hedged UCITS ETF",
    "IWDE.MI":   "iShares MSCI World EUR Hedged UCITS ETF",
    "JRGE.MI":   "JPMorgan Global Research Enhanced Index ETF",
    "SEMA.MI":   "iShares MSCI EM UCITS ETF EUR Acc",
    "NQSE.DE":   "iShares NASDAQ 100 UCITS ETF",
    "XDEE.DE":   "Xtrackers S&P 500 Equal Weight EUR Hedged",
    "EST.MI":    "Amundi MSCI Eastern Europe Ex Russia UCITS ETF",
    "LAFRI.MI":  "Amundi Pan Africa UCITS ETF",
    "CSEMAS.MI": "iShares MSCI EM Asia ETF EUR Acc",
    "WS5X.MI":   "WisdomTree EURO STOXX 50",
    "WWRD.MI":   "WisdomTree MSCI World Quality Dividend Growth",
    "WSPE.MI":   "WisdomTree S&P 500 EUR Hedged",
    "WNAS.MI":   "WisdomTree NASDAQ-100 ETP",
    "NTSZ.DE":   "Neuberger Berman US Multi Cap Opportunities",
    "NTSG.MI":   "Neuberger Berman Sustainable Global Equity",
    "NTSX.MI":   "WisdomTree US Efficient Core",
    "LMVC.MI":   "Amundi MSCI World Min Volatility Factor UCITS ETF",
}

# ─────────────────────────────────────────────────────────────────────────────
# HELPERS
# ─────────────────────────────────────────────────────────────────────────────

def now_ts():
    return datetime.now(ROME_TZ).strftime("%Y-%m-%d %H:%M CET")

# ─────────────────────────────────────────────────────────────────────────────
# INDICATORI
# ─────────────────────────────────────────────────────────────────────────────

def ema(values, period):
    k = 2 / (period + 1)
    result = [values[0]]
    for v in values[1:]:
        result.append(v * k + result[-1] * (1 - k))
    return result

def kama(prices, n=10, fast=2, slow=30):
    fast_sc = 2 / (fast + 1)
    slow_sc = 2 / (slow + 1)
    result  = list(prices[:n])
    for i in range(n, len(prices)):
        direction  = abs(prices[i] - prices[i - n])
        volatility = sum(abs(prices[j] - prices[j-1]) for j in range(i-n+1, i+1))
        er  = direction / volatility if volatility > 0 else 0
        sc  = (er * (fast_sc - slow_sc) + slow_sc) ** 2
        result.append(result[-1] + sc * (prices[i] - result[-1]))
    return result

def calc_er(prices, n=10):
    if len(prices) < n + 1: return 0.0
    direction  = abs(prices[-1] - prices[-n-1])
    volatility = sum(abs(prices[i] - prices[i-1]) for i in range(-n, 0))
    return round(direction / volatility if volatility > 0 else 0.0, 4)

def calc_ao(high, low):
    mid = [(h + l) / 2 for h, l in zip(high, low)]
    if len(mid) < 34: return 0.0, 0, []
    series = []
    for i in range(33, len(mid)):
        series.append(sum(mid[i-4:i+1])/5 - sum(mid[i-33:i+1])/34)
    baff = 0
    for i in range(len(series)-1, 0, -1):
        if series[i] > series[i-1]: baff += 1
        else: break
    return round(series[-1], 6), baff, series

def calc_rsi(prices, n=14):
    if len(prices) < n + 1: return 50.0
    d  = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    g  = [max(x, 0) for x in d]
    l  = [max(-x, 0) for x in d]
    ag, al = sum(g[:n])/n, sum(l[:n])/n
    for i in range(n, len(g)):
        ag = (ag*(n-1) + g[i]) / n
        al = (al*(n-1) + l[i]) / n
    rs = ag / al if al > 0 else 100
    return round(100 - 100/(1+rs), 1)

def calc_rsi_series(prices, n=14):
    if len(prices) < n + 1: return [None] * len(prices)
    d  = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    g  = [max(x, 0) for x in d]
    l_ = [max(-x, 0) for x in d]
    result = [None] * (n + 1)
    ag = sum(g[:n]) / n
    al = sum(l_[:n]) / n
    rs = ag / al if al > 0 else 100
    result.append(round(100 - 100/(1+rs), 2))
    for i in range(n, len(g)):
        ag = (ag*(n-1) + g[i]) / n
        al = (al*(n-1) + l_[i]) / n
        rs = ag / al if al > 0 else 100
        result.append(round(100 - 100/(1+rs), 2))
    return result

def calc_atr(high, low, close, n=14):
    if len(close) < 2: return 0.0
    tr = [max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1]))
          for i in range(1, len(close))]
    if not tr: return 0.0
    av = sum(tr[:n]) / min(n, len(tr))
    for i in range(min(n, len(tr)), len(tr)):
        av = (av*(n-1) + tr[i]) / n
    return round(av, 5)

def calc_parabolic_sar(high, low, af0=0.02, af_max=0.2):
    if len(high) < 5: return low[-1], True, [], []
    sar, ep, af, bull = low[0], high[0], af0, True
    sars, bulls = [sar], [True]
    for i in range(1, len(high)):
        prev = sars[-1]
        if bull:
            new   = prev + af * (ep - prev)
            cands = low[max(0,i-2):i]
            new   = min(new, min(cands)) if cands else new
            if low[i] < new:
                bull, new, ep, af = False, ep, low[i], af0
            else:
                if high[i] > ep: ep = high[i]; af = min(af+af0, af_max)
        else:
            new   = prev + af * (ep - prev)
            cands = high[max(0,i-2):i]
            new   = max(new, max(cands)) if cands else new
            if high[i] > new:
                bull, new, ep, af = True, ep, high[i], af0
            else:
                if low[i] < ep: ep = low[i]; af = min(af+af0, af_max)
        sars.append(new); bulls.append(bull)
    return round(sars[-1], 5), bulls[-1], bulls, sars

def trendycator(close):
    if len(close) < 55: return "GRIGIO"
    e21, e55 = ema(close, 21), ema(close, 55)
    if close[-1] > e21[-1] > e55[-1]: return "VERDE"
    if close[-1] < e21[-1] < e55[-1]: return "ROSSO"
    return "GRIGIO"

def mm_align(close):
    if len(close) < 200: return False
    return close[-1] > sum(close[-20:])/20 > sum(close[-50:])/50 > sum(close[-200:])/200

def calc_vortex(high, low, close, n=14):
    if len(close) < n + 1: return 1.0, 1.0, False
    vm_plus  = [abs(high[i] - low[i-1])  for i in range(1, len(close))]
    vm_minus = [abs(low[i]  - high[i-1]) for i in range(1, len(close))]
    tr       = [max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1]))
                for i in range(1, len(close))]
    vi_plus  = round(sum(vm_plus[-n:])  / sum(tr[-n:]) if sum(tr[-n:])>0 else 1.0, 4)
    vi_minus = round(sum(vm_minus[-n:]) / sum(tr[-n:]) if sum(tr[-n:])>0 else 1.0, 4)
    return vi_plus, vi_minus, vi_plus > vi_minus

def calc_rvi(close, open_, high, low, n=10):
    if len(close) < n + 4: return 0.0, 0.0, False
    num, den = [], []
    for i in range(3, len(close)):
        num.append((close[i]-open_[i] + 2*(close[i-1]-open_[i-1])
                    + 2*(close[i-2]-open_[i-2]) + (close[i-3]-open_[i-3])) / 6)
        den.append((high[i]-low[i] + 2*(high[i-1]-low[i-1])
                    + 2*(high[i-2]-low[i-2]) + (high[i-3]-low[i-3])) / 6)
    if len(num) < n: return 0.0, 0.0, False
    rvi_s = []
    for i in range(n-1, len(num)):
        d = sum(den[i-n+1:i+1])
        rvi_s.append(sum(num[i-n+1:i+1]) / d if d != 0 else 0)
    if len(rvi_s) < 4: return 0.0, 0.0, False
    sig = [(rvi_s[i] + 2*rvi_s[i-1] + 2*rvi_s[i-2] + rvi_s[i-3])/6
           for i in range(3, len(rvi_s))]
    if not sig: return 0.0, 0.0, False
    return round(rvi_s[-1], 6), round(sig[-1], 6), rvi_s[-1] > sig[-1]

# ─────────────────────────────────────────────────────────────────────────────
# REGIME
# ─────────────────────────────────────────────────────────────────────────────

def calc_hurst(prices, min_points=30):
    if len(prices) < min_points: return 0.5
    lags = [l for l in [2,4,8,16,32] if l < len(prices)//2]
    if len(lags) < 3: return 0.5
    log_p = [math.log(p) for p in prices if p > 0]
    if len(log_p) < max(lags)+1: return 0.5
    vars_ = []
    for lag in lags:
        diffs = [log_p[i]-log_p[i-lag] for i in range(lag, len(log_p))]
        if not diffs: return 0.5
        mean_d = sum(diffs)/len(diffs)
        var = sum((d-mean_d)**2 for d in diffs)/len(diffs)
        vars_.append(var if var > 0 else 1e-10)
    log_lags = [math.log(l) for l in lags]
    log_vars = [math.log(v) for v in vars_]
    n = len(lags)
    mx = sum(log_lags)/n; my = sum(log_vars)/n
    num = sum((log_lags[i]-mx)*(log_vars[i]-my) for i in range(n))
    den = sum((log_lags[i]-mx)**2 for i in range(n))
    if den == 0: return 0.5
    return round(max(0.1, min(0.9, num/den/2)), 3)

def calc_adx_full(high, low, close, n=14):
    if len(close) < n+2: return 20.0, 25.0, 20.0
    tr_list, pdm_list, ndm_list = [], [], []
    for i in range(1, len(close)):
        tr_list.append(max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1])))
        up = high[i]-high[i-1]; dn = low[i-1]-low[i]
        pdm_list.append(up if up>dn and up>0 else 0.0)
        ndm_list.append(dn if dn>up and dn>0 else 0.0)
    atr14 = ema(tr_list, n)
    pdi14 = [100*p/(a+1e-10) for p,a in zip(ema(pdm_list,n), atr14)]
    ndi14 = [100*nd/(a+1e-10) for nd,a in zip(ema(ndm_list,n), atr14)]
    dx    = [100*abs(p-nd)/(p+nd+1e-10) for p,nd in zip(pdi14,ndi14)]
    adx14 = ema(dx, n)
    return round(float(adx14[-1]),1), round(float(pdi14[-1]),1), round(float(ndi14[-1]),1)

def classify_regime(h60, h1y, adx, pdi, ndi):
    if adx >= 25:
        if pdi >= ndi:
            if h60 > 0.55:
                return {"code":"SLANCIO","label":"🚀 Slancio","color":"#1a7f37","desc":"Trend rialzista forte"}
            return {"code":"SALITA","label":"📈 Salita","color":"#2ea043","desc":"Rialzo in corso"}
        return {"code":"RIBASSO","label":"📉 Ribasso","color":"#cf222e","desc":"Ribasso in corso"}
    elif adx >= 20:
        return {"code":"TRANSIZIONE","label":"⚠️ Transizione","color":"#bc4c00","desc":"Zona grigia"}
    return {"code":"LATERALE","label":"↔ Laterale","color":"#8c98a4","desc":"Senza direzione"}

# ─────────────────────────────────────────────────────────────────────────────
# SIGNALS HISTORY — salva/legge da data/signals/TICKER.json
# ─────────────────────────────────────────────────────────────────────────────

def load_signal_history(ticker):
    path = f"data/signals/{ticker}.json"
    if os.path.exists(path):
        try:
            with open(path) as f:
                return json.load(f)
        except:
            pass
    return {"ticker": ticker, "history": []}

def save_signal_history(ticker, history_data):
    os.makedirs("data/signals", exist_ok=True)
    path = f"data/signals/{ticker}.json"
    with open(path, "w") as f:
        json.dump(history_data, f, separators=(",",":"), default=str)

def update_signal_history(ticker, new_level, price, score, er):
    """Aggiunge un evento alla storia segnali solo se il livello è cambiato."""
    data = load_signal_history(ticker)
    history = data.get("history", [])
    last_level = history[-1]["signal"] if history else None
    if new_level != last_level:
        history.append({
            "date":   now_ts()[:10],
            "ts":     now_ts(),
            "signal": new_level,
            "price":  round(float(price), 4) if price else None,
            "score":  round(float(score), 1) if score else None,
            "er":     round(float(er), 4) if er else None,
        })
        # mantieni ultimi 20 eventi
        history = history[-20:]
        data["history"] = history
        save_signal_history(ticker, data)
    return history

# ─────────────────────────────────────────────────────────────────────────────
# CHART JSON
# ─────────────────────────────────────────────────────────────────────────────

def save_chart_json(ticker, closes, highs, lows, dates,
                    ao_series_full, kama_series,
                    sar_series, sar_bull_series, rsi_series,
                    signals_history=None):
    os.makedirs("data/charts", exist_ok=True)
    n = min(252, len(closes))

    def fmt4(v): return round(float(v),4) if v is not None else None
    def fmt6(v): return round(float(v),6) if v is not None else None
    def fmt2(v): return round(float(v),2) if v is not None else None

    dates_out  = dates[-n:]
    closes_out = [fmt4(v) for v in closes[-n:]]
    highs_out  = [fmt4(v) for v in highs[-n:]]
    lows_out   = [fmt4(v) for v in lows[-n:]]
    kama_out   = [fmt4(v) for v in kama_series[-n:]]

    if len(ao_series_full) >= n:
        ao_out = [fmt6(v) for v in ao_series_full[-n:]]
    else:
        ao_out = [None]*(n-len(ao_series_full)) + [fmt6(v) for v in ao_series_full]

    if len(rsi_series) >= n:
        rsi_out = [fmt2(v) for v in rsi_series[-n:]]
    else:
        rsi_out = [None]*(n-len(rsi_series)) + [fmt2(v) for v in rsi_series]

    if len(sar_series) >= n:
        sar_out      = [fmt4(v) for v in sar_series[-n:]]
        sar_bull_out = [bool(v) for v in sar_bull_series[-n:]]
    else:
        pad = n - len(sar_series)
        sar_out      = [None]*pad + [fmt4(v) for v in sar_series]
        sar_bull_out = [True]*pad + [bool(v) for v in sar_bull_series]

    baff_out = []
    count = 0
    for i, v in enumerate(ao_out):
        if v is None or i == 0 or ao_out[i-1] is None:
            baff_out.append(0); count = 0; continue
        if v > ao_out[i-1]:   count = count+1 if count >= 0 else 1
        elif v < ao_out[i-1]: count = count-1 if count <= 0 else -1
        else:                  count = 0
        baff_out.append(abs(count))

    nc = len(closes)
    mom1m = round((closes[-1]/closes[-22]-1)*100,2) if nc>=22 else None
    mom3m = round((closes[-1]/closes[-63]-1)*100,2) if nc>=63 else None
    mom6m = round((closes[-1]/closes[-126]-1)*100,2) if nc>=126 else None

    fname = f"data/charts/{ticker}.json"
    with open(fname, "w") as f:
        json.dump({
            "ticker":          ticker,
            "dates":           dates_out,
            "closes":          closes_out,
            "highs":           highs_out,
            "lows":            lows_out,
            "kama":            kama_out,
            "ao":              ao_out,
            "rsi":             rsi_out,
            "sar":             sar_out,
            "sar_bull":        sar_bull_out,
            "baff":            baff_out,
            "mom1m":           mom1m,
            "mom3m":           mom3m,
            "mom6m":           mom6m,
            "signals_history": signals_history or [],
            "generated_at":    now_ts(),
        }, f, separators=(",",":"), default=str)

# ─────────────────────────────────────────────────────────────────────────────
# SCORE
# ─────────────────────────────────────────────────────────────────────────────

def calc_score(er, baff, k_pct, p7, p30, mm_ok, ao_pos, cross, trend,
               vortex_bull=False, rvi_bull=False):
    s  = er * 30
    s += min(baff, 5) * 4
    s += max(-10, min(10, p7)) * 1.0
    s += max(-5,  min(5,  p30)) * 0.5
    if k_pct > 0: s += min(k_pct, 3)
    s += {True: 7}.get(cross <= 3, 5 if cross <= 10 else 2 if cross <= 20 else 0)
    s += {"VERDE": 10, "GRIGIO": 5}.get(trend, 0)
    if mm_ok:       s += 3
    if ao_pos:      s += 2
    if vortex_bull: s += 5
    if rvi_bull:    s += 5
    if trend == "ROSSO": s *= 0.6
    return round(max(0, min(100, s)), 1)

# ─────────────────────────────────────────────────────────────────────────────
# BUY LEVEL
# ─────────────────────────────────────────────────────────────────────────────

def eval_buy_level(c, vix_regime):
    price      = c["price"]
    kama_v     = c["kama"]
    er         = c["er"]
    ao_val     = c["ao"]
    ao_series  = c.get("ao_series", [])
    sar_bull   = c["sar_bullish"]
    score      = c["score"]
    vortex_b   = c.get("vortex_bullish", False)
    rvi_b      = c.get("rvi_bullish", False)
    trend      = c["trend"]
    above_kama = price > kama_v
    cross_bars = c.get("cross_bars", 99)

    if (vix_regime == "NORMALE"
            and score >= 80 and er > 0.6
            and c.get("baffetti", 0) >= 3
            and vortex_b and rvi_b
            and above_kama and sar_bull
            and trend == "VERDE"):
        return "BUY3"

    if (vix_regime in ("NORMALE", "RIDOTTO")
            and above_kama and sar_bull
            and ao_val > 0 and score >= 65 and er >= 0.5):
        return "BUY2"

    if (vix_regime == "NORMALE" and above_kama and er > 0.4
            and sar_bull and cross_bars <= 5):
        ao_improving = len(ao_series) >= 3 and ao_series[-1] > ao_series[-2]
        if ao_improving:
            return "BUY1"

    # Segnali di uscita / debolezza
    stress = c.get("stress_score", 0)
    if stress >= 3 or (c["k_pct"] < 0 and trend == "ROSSO"):
        return "SELL"

    return "WATCH"

# ─────────────────────────────────────────────────────────────────────────────
# VIX
# ─────────────────────────────────────────────────────────────────────────────

def get_vix_regime():
    try:
        df = yf.download("^VIX", period="5d", interval="1d", progress=False, auto_adjust=True)
        if df is None or df.empty: return "NORMALE", None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        vix = float(df["Close"].dropna().iloc[-1])
        regime = "STOP" if vix > 25 else "RIDOTTO" if vix > 20 else "NORMALE"
        print(f"  VIX={vix:.1f} → {regime}")
        return regime, round(vix, 2)
    except Exception as e:
        print(f"  ⚠️  VIX error: {e}")
        return "NORMALE", None

def fetch_benchmark():
    try:
        df = yf.download(BENCHMARK, period="1y", interval="1d", progress=False, auto_adjust=True)
        if df is None or df.empty: return []
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return [float(x) for x in df["Close"].dropna().tolist()]
    except:
        return []

# ─────────────────────────────────────────────────────────────────────────────
# ANALYZE
# ─────────────────────────────────────────────────────────────────────────────

def analyze(ticker, name, bench_close, vix_regime):
    try:
        df = yf.download(ticker, period="1y", interval="1d", progress=False, auto_adjust=True)
        if df is None or df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.loc[:, ~df.columns.duplicated()].dropna(subset=["Close","High","Low"])
        if len(df) < 55: return None

        close  = [float(x) for x in df["Close"].tolist()]
        high   = [float(x) for x in df["High"].tolist()]
        low    = [float(x) for x in df["Low"].tolist()]
        open_  = [float(x) for x in df["Open"].tolist()] if "Open" in df.columns else close[:]
        dates  = [str(d.date()) for d in df.index]

        price   = close[-1]
        kama_s  = kama(close)
        kama_v  = kama_s[-1]
        k_pct   = round((price/kama_v - 1)*100 if kama_v else 0, 2)
        er      = calc_er(close)
        ao_val, baff, ao_series = calc_ao(high, low)
        rsi_v   = calc_rsi(close)
        atr_v   = calc_atr(high, low, close)
        trend   = trendycator(close)
        mm_ok   = mm_align(close)
        sar_v, sar_bull, sar_history, sar_series_full = calc_parabolic_sar(high, low)
        vi_plus, vi_minus, vortex_bull = calc_vortex(high, low, close)
        rvi_val, rvi_sig, rvi_bull     = calc_rvi(close, open_, high, low)
        p7  = round((price/close[-8]  - 1)*100 if len(close) >= 8  else 0, 2)
        p30 = round((price/close[-31] - 1)*100 if len(close) >= 31 else 0, 2)

        cross = 0
        for i in range(len(kama_s)-1, 0, -1):
            if (close[i] > kama_s[i]) == (close[-1] > kama_v): cross += 1
            else: break

        rs_above_kama_rs = False
        trend_rs = "GRIGIO"
        if bench_close and len(bench_close) >= 20:
            n2  = min(len(close), len(bench_close))
            sc  = close[-n2:]; bw = bench_close[-n2:]
            rs_v = [c/b if b>0 else None for c,b in zip(sc,bw)]
            rc   = [v for v in rs_v if v is not None]
            if len(rc) >= 10:
                kama_rs          = kama(rc)
                rs_above_kama_rs = rc[-1] > kama_rs[-1]
                trend_rs         = trendycator(rc)

        score = calc_score(er, baff, k_pct, p7, p30, mm_ok, ao_val > 0, cross, trend,
                           vortex_bull, rvi_bull)

        ao_weakening = len(ao_series) >= 3 and ao_series[-1] < ao_series[-2] < ao_series[-3]
        stress_flags = []
        if k_pct < 0:      stress_flags.append("KAMA rotta")
        if not sar_bull:   stress_flags.append("SAR bear")
        if ao_val < 0:     stress_flags.append("AO negativo")
        elif ao_weakening: stress_flags.append("AO calante")
        if er < 0.4:       stress_flags.append("ER<0.4")

        h60  = calc_hurst(close[-60:]) if len(close) >= 60 else 0.5
        h1y  = calc_hurst(close)
        adx_val, pdi_val, ndi_val = calc_adx_full(high, low, close)
        regime = classify_regime(h60, h1y, adx_val, pdi_val, ndi_val)

        # Segnale BUY/SELL/WATCH
        buy_level = eval_buy_level({
            "price": price, "kama": kama_v, "er": er, "ao": ao_val,
            "ao_series": ao_series[-5:], "sar_bullish": sar_bull,
            "score": score, "vortex_bullish": vortex_bull, "rvi_bullish": rvi_bull,
            "trend": trend, "k_pct": k_pct, "baffetti": baff,
            "cross_bars": cross, "stress_score": len(stress_flags),
        }, vix_regime)

        # Aggiorna storia segnali
        signals_history = update_signal_history(ticker, buy_level, price, score, er)

        # Serie complete per il grafico
        rsi_series_full = calc_rsi_series(close)
        ao_series_padded = [None]*33 + ao_series

        # Salva chart JSON con storia segnali integrata
        try:
            save_chart_json(
                ticker          = ticker,
                closes          = close,
                highs           = high,
                lows            = low,
                dates           = dates,
                ao_series_full  = ao_series_padded,
                kama_series     = kama_s,
                sar_series      = sar_series_full,
                sar_bull_series = sar_history,
                rsi_series      = rsi_series_full,
                signals_history = signals_history,
            )
        except Exception as ce:
            print(f"  ⚠️  chart JSON {ticker}: {ce}")

        return {
            "ticker": ticker, "name": name,
            "price": round(price,3), "kama": round(kama_v,3), "k_pct": k_pct,
            "er": er, "ao": round(ao_val,6),
            "ao_series": [round(x,6) for x in ao_series[-5:]],
            "baffetti": baff, "rsi": rsi_v,
            "atr": atr_v,
            "trend": trend, "mm_aligned": mm_ok,
            "sar": sar_v, "sar_bullish": sar_bull,
            "sar_history": sar_history[-5:],
            "vi_plus": vi_plus, "vi_minus": vi_minus, "vortex_bullish": vortex_bull,
            "rvi": rvi_val, "rvi_signal": rvi_sig, "rvi_bullish": rvi_bull,
            "perf7": p7, "perf30": p30,
            "rs_above_kama": rs_above_kama_rs, "trend_rs": trend_rs,
            "score": score, "cross_bars": cross,
            "stress_flags": stress_flags,
            "stress_score": len(stress_flags),
            "hurst_60": h60, "hurst_1y": h1y, "adx": adx_val,
            "regime": regime,
            "buy_level": buy_level,
            "level_ts": now_ts(),
        }
    except Exception as e:
        print(f"  ✗ {ticker}: {e}")
        return None

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    now       = datetime.now(ROME_TZ)
    print(f"🦅 RAPTOR GEOGRAFIA v6 — {now.strftime('%d/%m/%Y %H:%M')} CET")

    os.makedirs("data/charts",  exist_ok=True)
    os.makedirs("data/signals", exist_ok=True)

    print("\n📊 VIX...")
    vix_regime, vix_val = get_vix_regime()

    print(f"\n📊 Benchmark {BENCHMARK}...")
    bench = fetch_benchmark()
    print(f"  {'✓' if bench else '✗'} {len(bench)} barre")

    print("\n📊 PAESI...")
    paesi_data = []
    for t, n in PAESI.items():
        print(f"  {t}...", end=" ", flush=True)
        r = analyze(t, n, bench, vix_regime)
        if r:
            paesi_data.append(r)
            print(f"✓ {r['buy_level']} score={r['score']}")
        else:
            print("✗")

    print("\n📊 NEW AREA...")
    new_area_data = []
    for t, n in NEW_AREA.items():
        print(f"  {t}...", end=" ", flush=True)
        r = analyze(t, n, bench, vix_regime)
        if r:
            new_area_data.append(r)
            print(f"✓ {r['buy_level']} score={r['score']}")
        else:
            print("✗")

    # Top 10 watchlist = BUY2/BUY3 per score
    def top10(data):
        active = [d for d in data if d["buy_level"] in ("BUY1","BUY2","BUY3")]
        return sorted(active, key=lambda x: x["score"], reverse=True)[:10]

    output = {
        "updated_at":      now.isoformat(),
        "updated_display": now.strftime("%d/%m/%Y %H:%M CET"),
        "vix":             vix_val,
        "vix_regime":      vix_regime,
        "paesi": {
            "all":       sorted(paesi_data,    key=lambda x: x["score"], reverse=True),
            "watchlist": top10(paesi_data),
        },
        "new_area": {
            "all":       sorted(new_area_data, key=lambda x: x["score"], reverse=True),
            "watchlist": top10(new_area_data),
        },
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2, default=str)

    n_charts  = len([f for f in os.listdir("data/charts")  if f.endswith(".json")])
    n_signals = len([f for f in os.listdir("data/signals") if f.endswith(".json")])
    print(f"\n✅ {OUTPUT_FILE} aggiornato — {now.strftime('%d/%m/%Y %H:%M CET')}")
    print(f"   VIX     : {vix_regime}" + (f" ({vix_val})" if vix_val else ""))
    print(f"   PAESI   : {len(paesi_data)} ticker")
    print(f"   NEW AREA: {len(new_area_data)} ticker")
    print(f"   CHARTS  : {n_charts} JSON · SIGNALS: {n_signals} JSON")

if __name__ == "__main__":
    main()
