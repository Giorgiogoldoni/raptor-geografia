#!/usr/bin/env python3
"""
🦅 RAPTOR GEOGRAFIA — Autonomous ETF Portfolio Manager v5
Regole BUY1/BUY2/BUY3 + EXIT1/EXIT1b/EXIT2/EXIT3
Score ricalibrato 0-100 · VIX regime · RS Line vs benchmark
Cooldown 2gg · Event log con timestamp CET per ogni posizione

BUY1  🔵 Early Entry    (size 35%)     KAMA cross↑ · ER>0.4 · SAR bull · AO crescente
BUY2  🟢 Confirmation   (size 70%)     score≥65 · AO>0 · SAR bull · ER≥0.5
BUY3  🟢★ Full Entry    (size 100%)    score≥80 · ER>0.6 · BaffRS≥3 · RS>KAMA_RS · TrendRS=VERDE

EXIT1 🟡 Uscita parziale (40%)         SAR gira sopra · AO cala 2+ sessioni
EXIT1b⏱  Time Stop                      7gg in BUY1 senza upgrade a BUY2
EXIT2 🟠 Uscita forte   (75%)          score cala 10+pt dal picco AND ER<0.5
EXIT3 🔴 Uscita totale  (100%)         score<35 OR 2+ condizioni negative

VIX>25  → STOP (nessun ingresso)
VIX20-25→ RIDOTTO (solo BUY2/BUY3)
VIX<20  → NORMALE (tutti gli ingressi)
Fallback VIX non disponibile → NORMALE

Cooldown: 2gg dopo ogni uscita per quel ticker
Max posizioni: BUY1≤5 · BUY2≤3 · BUY3≤2
"""

import json, os
from datetime import datetime, date, timedelta
import pytz
import yfinance as yf
import pandas as pd

ROME_TZ       = pytz.timezone("Europe/Rome")
STATE_FILE    = "portfolio_state.json"
OUTPUT_FILE   = "geografia.json"
BENCHMARK     = "SWRD.MI"
XEON_TICKER   = "XEON.MI"

MAX_BUY1      = 5
MAX_BUY2      = 3
MAX_BUY3      = 2
COOLDOWN_DAYS = 2

# ─────────────────────────────────────────────────────────────────────────────
# ETF UNIVERSE
# ─────────────────────────────────────────────────────────────────────────────

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

def make_event(level, reason, size_pct=None, score=None, er=None):
    e = {"ts": now_ts(), "level": level, "reason": reason}
    if size_pct is not None: e["size_pct"] = size_pct
    if score    is not None: e["score"]    = round(float(score), 1)
    if er       is not None: e["er"]       = round(float(er), 4)
    return e

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
    if len(high) < 5: return low[-1], True, []
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
    return round(sars[-1], 5), bulls[-1], bulls

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
# SCORE 0-100
# ─────────────────────────────────────────────────────────────────────────────

def calc_score(er, baff, k_pct, p7, p30, mm_ok, ao_pos, cross, trend,
               vortex_bull=False, rvi_bull=False,
               rs_above_kama=False, trend_rs="GRIGIO"):
    """
    Componenti (max teorico ~112, clampato a 100):
      ER×30         = 0-30
      Baff(cap5)×4  = 0-20
      P7(cap±10)    = 0-10
      P30(cap±5)×0.5= 0-2.5
      K%(cap 0-3)   = 0-3
      Cross recente = 0-7
      Trendycator   = 0/5/10
      MM align      = 0/3
      AO positivo   = 0/2
      Vortex bull   = 0/5
      RVI bull      = 0/5
      RS>KAMA_RS    = 0/5
      Trend RS verde= 0/5
    Penalità Trendycator ROSSO: ×0.6
    """
    s  = er * 30
    s += min(baff, 5) * 4
    s += max(-10, min(10, p7)) * 1.0
    s += max(-5,  min(5,  p30)) * 0.5
    if k_pct > 0: s += min(k_pct, 3)
    s += {True: 7}.get(cross <= 3, 5 if cross <= 10 else 2 if cross <= 20 else 0)
    s += {"VERDE": 10, "GRIGIO": 5}.get(trend, 0)
    if mm_ok:        s += 3
    if ao_pos:       s += 2
    if vortex_bull:  s += 5
    if rvi_bull:     s += 5
    if rs_above_kama:s += 5
    if trend_rs == "VERDE": s += 5
    if trend == "ROSSO": s *= 0.6
    return round(max(0, min(100, s)), 1)

# ─────────────────────────────────────────────────────────────────────────────
# VIX REGIME
# ─────────────────────────────────────────────────────────────────────────────

def get_vix_regime():
    try:
        df = yf.download("^VIX", period="5d", interval="1d",
                         progress=False, auto_adjust=True)
        if df is None or df.empty:
            print("  ⚠️  VIX non disponibile — fallback NORMALE")
            return "NORMALE", None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        vix = float(df["Close"].dropna().iloc[-1])
        regime = "STOP" if vix > 25 else "RIDOTTO" if vix > 20 else "NORMALE"
        print(f"  VIX={vix:.1f} → {regime}")
        return regime, round(vix, 2)
    except Exception as e:
        print(f"  ⚠️  VIX error: {e} — fallback NORMALE")
        return "NORMALE", None

# ─────────────────────────────────────────────────────────────────────────────
# BENCHMARK E ANALISI ETF
# ─────────────────────────────────────────────────────────────────────────────

def fetch_benchmark():
    try:
        df = yf.download(BENCHMARK, period="1y", interval="1d",
                         progress=False, auto_adjust=True)
        if df is None or df.empty: return []
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        return [float(x) for x in df["Close"].dropna().tolist()]
    except:
        return []

def analyze(ticker, name, bench_close):
    try:
        df = yf.download(ticker, period="1y", interval="1d",
                         progress=False, auto_adjust=True)
        if df is None or df.empty: return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.loc[:, ~df.columns.duplicated()].dropna(subset=["Close","High","Low"])
        if len(df) < 55: return None

        close  = [float(x) for x in df["Close"].tolist()]
        high   = [float(x) for x in df["High"].tolist()]
        low    = [float(x) for x in df["Low"].tolist()]
        open_  = [float(x) for x in df["Open"].tolist()] if "Open" in df.columns else close[:]

        price   = close[-1]
        kama_s  = kama(close)
        kama_v  = kama_s[-1]
        k_pct   = round((price/kama_v - 1)*100 if kama_v else 0, 2)
        er      = calc_er(close)
        ao_val, baff, ao_series = calc_ao(high, low)
        rsi_v   = calc_rsi(close)
        atr_v   = calc_atr(high, low, close)
        trail   = round(price - 2*atr_v, 3)
        trend   = trendycator(close)
        mm_ok   = mm_align(close)
        sar_v, sar_bull, sar_history = calc_parabolic_sar(high, low)
        vi_plus, vi_minus, vortex_bull = calc_vortex(high, low, close)
        rvi_val, rvi_sig, rvi_bull     = calc_rvi(close, open_, high, low)
        p7  = round((price/close[-8]  - 1)*100 if len(close) >= 8  else 0, 2)
        p30 = round((price/close[-31] - 1)*100 if len(close) >= 31 else 0, 2)

        # Cross: barre consecutive nello stesso lato di KAMA
        cross = 0
        for i in range(len(kama_s)-1, 0, -1):
            if (close[i] > kama_s[i]) == (close[-1] > kama_v): cross += 1
            else: break

        # RS Line vs benchmark
        rs_above_kama_rs = False
        trend_rs         = "GRIGIO"
        baff_rs          = 0
        rs_line          = None
        if bench_close and len(bench_close) >= 20:
            n2   = min(len(close), len(bench_close))
            sc   = close[-n2:]
            bw   = bench_close[-n2:]
            rs_v = [c/b if b > 0 else None for c, b in zip(sc, bw)]
            rc   = [v for v in rs_v if v is not None]
            if len(rc) >= 10:
                rs_line          = rs_v[-1]
                kama_rs          = kama(rc)
                rs_above_kama_rs = rc[-1] > kama_rs[-1]
                trend_rs         = trendycator(rc)
                for i in range(len(rc)-1, 0, -1):
                    if rc[i] > rc[i-1]: baff_rs += 1
                    else: break

        score = calc_score(er, baff, k_pct, p7, p30, mm_ok, ao_val > 0, cross, trend,
                           vortex_bull, rvi_bull, rs_above_kama_rs, trend_rs)

        # ── Stress flags (condizioni di difficoltà) ──────────────────────────
        ao_weakening = len(ao_series) >= 3 and ao_series[-1] < ao_series[-2] < ao_series[-3]
        stress_flags = []
        if k_pct < 0:        stress_flags.append("KAMA rotta")
        if not sar_bull:     stress_flags.append("SAR bear")
        if ao_val < 0:       stress_flags.append("AO negativo")
        elif ao_weakening:   stress_flags.append("AO calante")
        if er < 0.4:         stress_flags.append("ER<0.4")
        stress_score = len(stress_flags)

        result = {
            "ticker": ticker, "name": name,
            "price": round(price, 3), "kama": round(kama_v, 3), "k_pct": k_pct,
            "er": er, "ao": round(ao_val, 6),
            "ao_series": [round(x, 6) for x in ao_series[-5:]],
            "baffetti": baff, "rsi": rsi_v,
            "atr": atr_v, "trailing_stop": trail,
            "trend": trend, "mm_aligned": mm_ok,
            "sar": sar_v, "sar_bullish": sar_bull,
            "sar_history": sar_history[-5:],
            "vi_plus": vi_plus, "vi_minus": vi_minus, "vortex_bullish": vortex_bull,
            "rvi": rvi_val, "rvi_signal": rvi_sig, "rvi_bullish": rvi_bull,
            "perf7": p7, "perf30": p30,
            "rs_line": round(rs_line, 6) if rs_line else None,
            "rs_above_kama": rs_above_kama_rs,
            "trend_rs": trend_rs, "baff_rs": baff_rs,
            "score": score, "cross_bars": cross,
            "stress_flags": stress_flags,
            "stress_score": stress_score,
            "buy_level": None,   # valorizzato dopo da calc_all_levels()
            "level_ts": None,    # timestamp primo segnale del livello
        }
        return result
    except Exception as e:
        print(f"  ✗ {ticker}: {e}")
        return None

# ─────────────────────────────────────────────────────────────────────────────
# SEGNALI BUY / EXIT
# ─────────────────────────────────────────────────────────────────────────────

def eval_buy_level(c, vix_regime):
    """
    Valuta il livello di BUY applicabile a un candidato (o None).
    Ritorna il livello più alto applicabile.
    """
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
    baff_rs    = c.get("baff_rs", 0)
    rs_kama    = c.get("rs_above_kama", False)
    trend_rs   = c.get("trend_rs", "GRIGIO")

    above_kama = price > kama_v

    # BUY3
    if (vix_regime == "NORMALE"
            and score >= 80 and er > 0.6
            and baff_rs >= 3 and rs_kama
            and trend_rs == "VERDE"
            and above_kama and sar_bull):
        return "BUY3"

    # BUY2
    if (vix_regime in ("NORMALE", "RIDOTTO")
            and above_kama and sar_bull
            and ao_val > 0 and score >= 65 and er >= 0.5):
        return "BUY2"

    # BUY1
    if (vix_regime == "NORMALE" and above_kama and er > 0.4 and sar_bull):
        ao_improving = len(ao_series) >= 3 and ao_series[-1] > ao_series[-2]
        if ao_improving:
            return "BUY1"

    return None

def eval_exit(pos, cur):
    """
    Valuta se attivare un EXIT.
    Ritorna (exit_level, reason) o (None, None).
    """
    score         = cur["score"]
    peak_score    = pos.get("peak_score", score)
    er            = cur["er"]
    ao_val        = cur["ao"]
    ao_series     = cur.get("ao_series", [])
    sar_history   = cur.get("sar_history", [])
    k_pct         = cur["k_pct"]
    current_level = pos.get("current_level", "BUY1")
    days_in_buy1  = pos.get("days_in_buy1", 0)

    # EXIT3 — totale
    neg = sum([k_pct < 0, ao_val < 0, er < 0.3, cur.get("perf30", 0) < -5])
    if score < 35:
        return "EXIT3", f"Score {score}<35 — uscita totale"
    if neg >= 2:
        r = []
        if k_pct < 0:                   r.append("KAMA rotta")
        if ao_val < 0:                   r.append("AO negativo")
        if er < 0.3:                     r.append(f"ER {er:.2f}<0.3")
        if cur.get("perf30", 0) < -5:    r.append("sottoperf 30gg<-5%")
        return "EXIT3", "2+ cond. negative: " + " · ".join(r)

    # EXIT2 — forte
    drop = peak_score - score
    if drop >= 10 and er < 0.5:
        return "EXIT2", f"Score -{ drop:.0f}pt ({peak_score:.0f}→{score:.0f}) · ER {er:.2f}<0.5"

    # EXIT1 — parziale: SAR gira + AO cala 2+ sessioni
    sar_flipped  = (len(sar_history) >= 2
                    and not sar_history[-1] and sar_history[-2])
    ao_weakening = (len(ao_series) >= 3
                    and ao_series[-1] < ao_series[-2] < ao_series[-3])
    if sar_flipped and ao_weakening:
        return "EXIT1", "SAR girato sopra prezzo · AO in calo 2+ sessioni"

    # EXIT1b — time stop
    if current_level == "BUY1" and days_in_buy1 >= 7:
        return "EXIT1b", f"Time stop: {days_in_buy1}gg in BUY1 senza upgrade a BUY2"

    return None, None

def calc_all_levels(etf_list, positions, vix_regime):
    """
    Per ogni ETF in etf_list valorizza buy_level e level_ts.
    - Se è in portafoglio: usa current_level + timestamp ultimo evento
    - Altrimenti: calcola eval_buy_level() in tempo reale
    """
    pos_map = {p["ticker"]: p for p in positions}
    for etf in etf_list:
        pos = pos_map.get(etf["ticker"])
        if pos:
            etf["buy_level"] = pos.get("current_level")
            evs = pos.get("events", [])
            etf["level_ts"]  = evs[-1]["ts"] if evs else pos.get("entry_ts", pos.get("entry_date"))
            # stress score aumentato se score calato dal picco
            peak = pos.get("peak_score", etf["score"])
            drop = peak - etf["score"]
            if drop >= 5:
                etf["stress_flags"] = etf.get("stress_flags", []) + [f"Score -{drop:.0f}pt dal picco"]
                etf["stress_score"] = len(etf["stress_flags"])
        else:
            lvl = eval_buy_level(etf, vix_regime)
            etf["buy_level"] = lvl
            etf["level_ts"]  = now_ts() if lvl else None

def buy_reason(level, c):
    if level == "BUY1":
        return (f"KAMA cross ↑ · ER {c['er']:.2f}>0.4 · SAR bull · AO crescente")
    if level == "BUY2":
        return (f"Score {c['score']}≥65 · AO {c['ao']:+.4f}>0 · ER {c['er']:.2f}≥0.5 · "
                f"SAR bull · Trend {c['trend']}")
    if level == "BUY3":
        return (f"Score {c['score']}≥80 · ER {c['er']:.2f}>0.6 · "
                f"BaffRS {c.get('baff_rs',0)}≥3 · RS>KAMA_RS · TrendRS {c.get('trend_rs','?')}")
    return ""

# ─────────────────────────────────────────────────────────────────────────────
# STATE
# ─────────────────────────────────────────────────────────────────────────────

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {
        "paesi":    {"positions": [], "history": [], "cooldowns": {}},
        "new_area": {"positions": [], "history": [], "cooldowns": {}},
    }

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)

# ─────────────────────────────────────────────────────────────────────────────
# PORTFOLIO UPDATE
# ─────────────────────────────────────────────────────────────────────────────

LEVEL_ORDER = {"BUY1": 1, "BUY2": 2, "BUY3": 3,
               "EXIT1": 0, "EXIT1b": 0, "EXIT2": 0, "EXIT3": 0}
SIZE_MAP    = {"BUY1": 35, "BUY2": 70, "BUY3": 100,
               "EXIT1": 40, "EXIT1b": 100, "EXIT2": 75, "EXIT3": 100}

def update_portfolio(existing, history, cooldowns, candidates, today_str, vix_regime):
    today     = date.fromisoformat(today_str)
    kept      = []
    exited    = []

    # Pulisci cooldown scaduti
    cooldowns = {k: v for k, v in cooldowns.items()
                 if date.fromisoformat(v) > today}

    # ── Aggiorna posizioni esistenti ─────────────────────────────────────────
    for pos in existing:
        cur = next((c for c in candidates if c["ticker"] == pos["ticker"]), None)
        if cur is None:
            pos["warning"] = "Dati non disponibili"
            kept.append(pos)
            continue

        entry_date    = date.fromisoformat(pos["entry_date"])
        days_held     = (today - entry_date).days
        cur_gain      = round((cur["price"] / pos["entry_price"] - 1) * 100, 2)
        new_trail     = round(cur["price"] - 2 * cur["atr"], 3)
        trail_stop    = max(pos.get("trailing_stop", new_trail), new_trail)
        current_level = pos.get("current_level", "BUY1")
        peak_score    = max(pos.get("peak_score", cur["score"]), cur["score"])
        days_in_buy1  = pos.get("days_in_buy1", 0) + (1 if current_level == "BUY1" else 0)
        events        = pos.get("events", [])

        # Verifica EXIT
        exit_level, exit_reason = eval_exit(
            {**pos, "peak_score": peak_score,
             "current_level": current_level, "days_in_buy1": days_in_buy1},
            cur
        )

        if exit_level in ("EXIT3", "EXIT1b"):
            # Uscita totale: chiude la posizione
            ev = make_event(exit_level, exit_reason,
                            size_pct=100, score=cur["score"], er=cur["er"])
            exited.append({
                **pos,
                "events":         events + [ev],
                "exit_level":     exit_level,
                "exit_reason":    exit_reason,
                "exit_price":     cur["price"],
                "final_gain_pct": cur_gain,
                "exit_date":      today_str,
                "exit_ts":        now_ts(),
            })
            cooldowns[pos["ticker"]] = (today + timedelta(days=COOLDOWN_DAYS)).isoformat()
            continue

        if exit_level in ("EXIT1", "EXIT2"):
            # Uscita parziale: aggiorna livello ma mantieni la posizione
            last_lvl = events[-1]["level"] if events else None
            if last_lvl != exit_level:
                ev = make_event(exit_level, exit_reason,
                                size_pct=SIZE_MAP[exit_level],
                                score=cur["score"], er=cur["er"])
                events.append(ev)
            current_level = exit_level
        else:
            # Nessun exit: verifica upgrade di livello
            new_level = eval_buy_level(cur, vix_regime)
            if new_level and LEVEL_ORDER.get(new_level, 0) > LEVEL_ORDER.get(current_level, 0):
                ev = make_event(new_level, buy_reason(new_level, cur),
                                size_pct=SIZE_MAP[new_level],
                                score=cur["score"], er=cur["er"])
                events.append(ev)
                current_level = new_level
                if new_level != "BUY1":
                    days_in_buy1 = 0

        # Target: BUY3 → trailing; altri → +5% fisso dall'ingresso
        target_price = pos.get("target_price", round(pos["entry_price"] * 1.05, 3))
        target_hit   = cur["price"] >= target_price

        pos.update({
            "current_price":    cur["price"],
            "current_gain_pct": cur_gain,
            "days_held":        days_held,
            "days_in_buy1":     days_in_buy1,
            "trailing_stop":    trail_stop,
            "target_price":     target_price,
            "target_hit":       target_hit,
            "current_level":    current_level,
            "peak_score":       peak_score,
            "score":            cur["score"],
            "er":               cur["er"],
            "trend":            cur["trend"],
            "sar_bullish":      cur["sar_bullish"],
            "vortex_bullish":   cur.get("vortex_bullish", False),
            "rvi_bullish":      cur.get("rvi_bullish", False),
            "rs_above_kama":    cur.get("rs_above_kama", False),
            "trend_rs":         cur.get("trend_rs", "GRIGIO"),
            "baff_rs":          cur.get("baff_rs", 0),
            "perf7":            cur["perf7"],
            "perf30":           cur["perf30"],
            "events":           events,
            "warning":          None,
        })
        kept.append(pos)

    # ── Nuovi ingressi ───────────────────────────────────────────────────────
    in_port   = {p["ticker"] for p in kept}
    count_b1  = sum(1 for p in kept if p.get("current_level") == "BUY1")
    count_b2  = sum(1 for p in kept if p.get("current_level") == "BUY2")
    count_b3  = sum(1 for p in kept if p.get("current_level") == "BUY3")

    new_cands = sorted(
        [c for c in candidates if c["ticker"] not in in_port
         and c["ticker"] not in cooldowns],
        key=lambda x: x["score"], reverse=True
    )

    for c in new_cands:
        lvl = eval_buy_level(c, vix_regime)
        if not lvl: continue
        if lvl == "BUY1" and count_b1 >= MAX_BUY1: continue
        if lvl == "BUY2" and count_b2 >= MAX_BUY2: continue
        if lvl == "BUY3" and count_b3 >= MAX_BUY3: continue

        ep    = c["price"]
        stop  = round(max(ep - 2*c["atr"], c["trailing_stop"]), 3)
        tgt   = round(ep * 1.05, 3)
        size  = SIZE_MAP[lvl]
        ev    = make_event(lvl, buy_reason(lvl, c),
                           size_pct=size, score=c["score"], er=c["er"])

        kept.append({
            "ticker":           c["ticker"],
            "name":             c["name"],
            "entry_date":       today_str,
            "entry_ts":         now_ts(),
            "entry_price":      ep,
            "current_price":    ep,
            "target_price":     tgt,
            "stop_loss":        stop,
            "trailing_stop":    stop,
            "current_gain_pct": 0.0,
            "days_held":        0,
            "days_in_buy1":     1 if lvl == "BUY1" else 0,
            "target_hit":       False,
            "current_level":    lvl,
            "size_pct":         size,
            "peak_score":       c["score"],
            "score":            c["score"],
            "er":               c["er"],
            "trend":            c["trend"],
            "sar_bullish":      c["sar_bullish"],
            "vortex_bullish":   c.get("vortex_bullish", False),
            "rvi_bullish":      c.get("rvi_bullish", False),
            "rs_above_kama":    c.get("rs_above_kama", False),
            "trend_rs":         c.get("trend_rs", "GRIGIO"),
            "baff_rs":          c.get("baff_rs", 0),
            "perf7":            c["perf7"],
            "perf30":           c["perf30"],
            "events":           [ev],
            "warning":          None,
        })

        if lvl == "BUY1": count_b1 += 1
        if lvl == "BUY2": count_b2 += 1
        if lvl == "BUY3": count_b3 += 1

    # Peso % per score
    tot = sum(p["score"] for p in kept)
    for p in kept:
        p["weight_pct"] = round(p["score"]/tot*100, 1) if tot else 0

    return kept, exited, cooldowns

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    now       = datetime.now(ROME_TZ)
    today_str = now.date().isoformat()
    print(f"🦅 RAPTOR GEOGRAFIA v5 — {now.strftime('%d/%m/%Y %H:%M')} CET")

    print("\n📊 VIX...")
    vix_regime, vix_val = get_vix_regime()

    print(f"\n📊 Benchmark {BENCHMARK}...")
    bench = fetch_benchmark()
    print(f"  {'✓' if bench else '✗'} {len(bench)} barre")

    state = load_state()

    print("\n📊 PAESI...")
    paesi_data = []
    for t, n in PAESI.items():
        print(f"  {t}...", end=" ", flush=True)
        r = analyze(t, n, bench)
        if r:
            paesi_data.append(r)
            print(f"✓ score={r['score']} er={r['er']:.2f}")
        else:
            print("✗")

    print("\n📊 NEW AREA...")
    new_area_data = []
    for t, n in NEW_AREA.items():
        print(f"  {t}...", end=" ", flush=True)
        r = analyze(t, n, bench)
        if r:
            new_area_data.append(r)
            print(f"✓ score={r['score']} er={r['er']:.2f}")
        else:
            print("✗")

    print("\n💰 XEON...")
    xeon = analyze(XEON_TICKER, "Xtrackers EUR Overnight Rate Swap UCITS ETF", bench)

    paesi_pos, paesi_ex, paesi_cd = update_portfolio(
        state["paesi"].get("positions", []),
        state["paesi"].get("history", []),
        state["paesi"].get("cooldowns", {}),
        paesi_data, today_str, vix_regime
    )
    new_pos, new_ex, new_cd = update_portfolio(
        state["new_area"].get("positions", []),
        state["new_area"].get("history", []),
        state["new_area"].get("cooldowns", {}),
        new_area_data, today_str, vix_regime
    )

    state["paesi"]["positions"]  = paesi_pos
    state["paesi"]["cooldowns"]  = paesi_cd
    state["paesi"].setdefault("history", []).extend(paesi_ex)
    state["new_area"]["positions"] = new_pos
    state["new_area"]["cooldowns"] = new_cd
    state["new_area"].setdefault("history", []).extend(new_ex)
    save_state(state)

    # Valorizza buy_level, level_ts, stress per TUTTI gli ETF (anche non in portafoglio)
    calc_all_levels(paesi_data,    paesi_pos, vix_regime)
    calc_all_levels(new_area_data, new_pos,   vix_regime)

    def top10_watch(data, positions):
        in_port = {p["ticker"] for p in positions}
        return sorted([d for d in data if d["ticker"] not in in_port],
                      key=lambda x: x["score"], reverse=True)[:10]

    output = {
        "updated_at":      now.isoformat(),
        "updated_display": now.strftime("%d/%m/%Y %H:%M CET"),
        "vix":             vix_val,
        "vix_regime":      vix_regime,
        "paesi": {
            "positions":     paesi_pos,
            "exited_today":  paesi_ex,
            "use_xeon":      len(paesi_pos) == 0,
            "xeon_price":    xeon["price"] if xeon else None,
            "watchlist":     top10_watch(paesi_data, paesi_pos),
            "all":           sorted(paesi_data, key=lambda x: x["score"], reverse=True),
            "cooldowns":     paesi_cd,
        },
        "new_area": {
            "positions":     new_pos,
            "exited_today":  new_ex,
            "use_xeon":      len(new_pos) == 0,
            "xeon_price":    xeon["price"] if xeon else None,
            "watchlist":     top10_watch(new_area_data, new_pos),
            "all":           sorted(new_area_data, key=lambda x: x["score"], reverse=True),
            "cooldowns":     new_cd,
        },
        "xeon": xeon,
    }

    with open(OUTPUT_FILE, "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n✅ {OUTPUT_FILE} aggiornato — {now.strftime('%d/%m/%Y %H:%M CET')}")
    print(f"   VIX  : {vix_regime}" + (f" ({vix_val})" if vix_val else " (fallback)"))
    print(f"   PAESI    : {len(paesi_pos)} pos | uscite oggi: {len(paesi_ex)}")
    print(f"   NEW AREA : {len(new_pos)} pos | uscite oggi: {len(new_ex)}")
    for lbl, positions in [("PAESI", paesi_pos), ("NEW AREA", new_pos)]:
        for p in positions:
            ev      = p.get("events", [])
            last_ts = ev[-1]["ts"] if ev else "—"
            print(f"   [{lbl}] {p['ticker']:12s} {p.get('current_level','?'):6s} "
                  f"score={p['score']:.0f} gain={p.get('current_gain_pct',0):+.1f}% "
                  f"last={last_ts}")

if __name__ == "__main__":
    main()
