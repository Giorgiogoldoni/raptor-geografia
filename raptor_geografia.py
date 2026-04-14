#!/usr/bin/env python3
"""
🦅 RAPTOR GEOGRAFIA — Autonomous ETF Portfolio Manager v4
Two portfolios: PAESI + NEW AREA (UCITS ETFs, all quoted in EUR on MI/DE/PA/AS)

Signal levels (Opzione C):
  LONG FORTE  = 7/7 conditions
  LONG        = 5-6/7 conditions
  EARLY FORTE = 4/7 conditions
  EARLY       = 3/7 conditions

Indicators: KAMA · ER · AO/Baffetti · Trendycator · SAR · Supertrend · MM
            + Vortex Index (VI+/VI-) · RVI (Relative Vigor Index)

Score bonuses: +5 Vortex bullish · +5 RVI bullish · -10 both bearish
Max positions : 7 per portfolio
Target        : +5% per trade · Time stop: 10 days
Cushion       : XEON when no ETF qualifies
"""

import json, os
from datetime import datetime, date
import pytz
import yfinance as yf
import pandas as pd

ROME_TZ = pytz.timezone("Europe/Rome")
MAX_POSITIONS = 7

# ─────────────────────────────────────────────────────────────────────────────
# ETF UNIVERSE — all EUR, quoted on MI / DE / PA / AS
# ─────────────────────────────────────────────────────────────────────────────

PAESI = {
    "IUSS.MI":    "iShares MSCI Saudi Arabia UCITS ETF",
    "SAUDI.MI":   "Franklin FTSE Saudi Arabia UCITS ETF",
    "IBZL.MI":    "iShares MSCI Brazil UCITS ETF",
    "XCHA.DE":    "Xtrackers CSI300 Swap UCITS ETF",
    "LCCN.MI":    "Amundi MSCI China UCITS ETF",
    "WSPE.MI":    "WisdomTree S&P 500 EUR Daily Hedged",
    "MCHN.MI":    "Invesco MSCI China All Shares UCITS ETF",
    "XCS3.DE":    "Xtrackers MSCI Malaysia UCITS ETF",
    "D5BI.DE":    "Xtrackers MSCI Mexico UCITS ETF",
    "FLXT.MI":    "Franklin FTSE Taiwan UCITS ETF",
    "TUR.PA":     "Amundi MSCI Turkey UCITS ETF",
    "XCS4.DE":    "Xtrackers MSCI Thailand UCITS ETF",
    "WRD.PA":     "HSBC MSCI World UCITS ETF",
    "IBCJ.MI":    "iShares MSCI Poland UCITS ETF",
    "XBAS.DE":    "Xtrackers MSCI Singapore UCITS ETF",
    "IMIB.MI":    "iShares FTSE MIB UCITS ETF",
    "WMIB.MI":    "WisdomTree FTSE MIB",
    "CN1.PA":     "Amundi MSCI Nordic UCITS ETF",
    "FMI.MI":     "Amundi Italy MIB ESG UCITS ETF",
    "CSMIB.MI":   "iShares FTSE MIB ETF EUR Acc",
    "SPXE.MI":    "State Street SPDR S&P 500 EUR Acc Hedged",
    "UKE.MI":     "UBS MSCI United Kingdom hEUR Acc",
    "WS5X.MI":    "WisdomTree EURO STOXX 50",
    "XSMI.MI":    "Xtrackers Switzerland UCITS ETF",
    "HSTE.MI":    "HSBC Hang Seng Tech UCITS ETF",
    "SP1E.MI":    "L&G S&P 100 Equal Weight UCITS ETF",
    "WSPX.MI":    "WisdomTree S&P 500",
    "LGUS.MI":    "L&G US Equity UCITS ETF",
    "SPY5.MI":    "State Street SPDR S&P 500 UCITS ETF",
    "VUSA.MI":    "Vanguard S&P 500 UCITS ETF",
    "DJE.PA":     "Amundi Dow Jones Industrial Average UCITS ETF",
    "SAUS.MI":    "iShares MSCI Australia UCITS ETF EUR",
    "FLXU.MI":    "Franklin U.S. Equity UCITS ETF",
    "SPXJ.MI":    "iShares MSCI Pacific ex-Japan UCITS ETF",
    "IS3U.DE":    "iShares MSCI France UCITS ETF",
    "XESD.DE":    "Xtrackers Spain UCITS ETF",
    "EXS1.DE":    "iShares Core DAX UCITS ETF",
    "XDAX.DE":    "Xtrackers DAX UCITS ETF",
    "INDO.PA":    "Amundi MSCI Indonesia UCITS ETF",
    "C40.PA":     "Amundi CAC 40 ESG UCITS ETF",
    "ITBL.MI":    "WisdomTree FTSE MIB Banks",
    "XPQP.DE":    "Xtrackers MSCI Philippines UCITS ETF",
    "FLXI.MI":    "Franklin FTSE India UCITS ETF",
    "XFVT.DE":    "Xtrackers Vietnam Swap UCITS ETF",
    "AUHEUA.MI":  "UBS MSCI Australia hEUR Acc",
    "VJPE.MI":    "Vanguard FTSE Japan EUR Hedged",
    "SRSA.MI":    "iShares MSCI South Africa UCITS ETF",
    "INDI.PA":    "Amundi MSCI India Swap UCITS ETF",
    "CSNDX.MI":   "iShares NASDAQ 100 UCITS ETF",
    "WNAS.MI":    "WisdomTree NASDAQ-100 ETP",
    "QTOP.MI":    "iShares Nasdaq 100 Top 30 UCITS ETF",
    "IAEX.AS":    "iShares AEX UCITS ETF",
    "XSFR.DE":    "Xtrackers S&P Select Frontier Swap UCITS ETF",
    "WRTY.MI":    "WisdomTree Russell 2000 ETP",
    "KOR.PA":     "Amundi MSCI Korea UCITS ETF",
    "GXDW.MI":    "Global X Dorsey Wright Thematic ETF",
    "NORW.MI":    "Global X MSCI Norway UCITS ETF",
    "LEER.DE":    "Xtrackers MSCI World Minimum Volatility UCITS ETF",
    "EST.MI":     "Amundi MSCI Eastern Europe Ex Russia UCITS ETF",
    "100H.MI":    "Amundi FTSE 100 EUR Hedged UCITS ETF",
    "SVE.MI":     "UBS MSCI Switzerland 20/35 UCITS ETF EUR",
}

NEW_AREA = {
    "ALAT.MI":    "Amundi MSCI EM Latin America UCITS ETF",
    "LTAM.MI":    "iShares MSCI EM Latin America UCITS ETF",
    "CSCA.MI":    "iShares MSCI Canada ETF EUR Acc",
    "IQQ9.DE":    "iShares BIC 50 UCITS ETF",
    "IAPD.MI":    "iShares Asia Pacific Dividend UCITS ETF",
    "CAHEUA.MI":  "UBS MSCI Canada UCITS ETF hEUR Acc",
    "IQQF.DE":    "iShares MSCI AC Far East ex-Japan UCITS ETF",
    "CSPXJ.MI":   "iShares Core MSCI Pac ex-Jpn ETF EUR Acc",
    "ISAC.MI":    "iShares MSCI ACWI UCITS ETF",
    "SXRU.DE":    "iShares Dow Jones Industrial Avg ETF EUR Acc",
    "SJPA.MI":    "iShares Core MSCI Japan IMI UCITS ETF",
    "MEUD.PA":    "Amundi Core Stoxx Europe 600 UCITS ETF",
    "IUSE.MI":    "iShares S&P 500 EUR Hedged UCITS ETF",
    "IJPE.MI":    "iShares MSCI Japan EUR Hedged UCITS ETF",
    "IWDE.MI":    "iShares MSCI World EUR Hedged UCITS ETF",
    "JRGE.MI":    "JPMorgan Global Research Enhanced Index ETF",
    "SEMA.MI":    "iShares MSCI EM UCITS ETF EUR Acc",
    "NQSE.DE":    "iShares NASDAQ 100 UCITS ETF",
    "XDEE.DE":    "Xtrackers S&P 500 Equal Weight EUR Hedged",
    "EST.MI":     "Amundi MSCI Eastern Europe Ex Russia UCITS ETF",
    "LAFRI.MI":   "Amundi Pan Africa UCITS ETF",
    "CSEMAS.MI":  "iShares MSCI EM Asia ETF EUR Acc",
    "WS5X.MI":    "WisdomTree EURO STOXX 50",
    "WWRD.MI":    "WisdomTree MSCI World Quality Dividend Growth",
    "WSPE.MI":    "WisdomTree S&P 500 EUR Hedged",
    "WNAS.MI":    "WisdomTree NASDAQ-100 ETP",
    "NTSZ.DE":    "Neuberger Berman US Multi Cap Opportunities",
    "NTSG.MI":    "Neuberger Berman Sustainable Global Equity",
    "NTSX.MI":    "WisdomTree US Efficient Core",
    "LMVC.MI":    "Amundi MSCI World Min Volatility Factor UCITS ETF",
}

XEON_TICKER = "XEON.MI"

# ─────────────────────────────────────────────────────────────────────────────
# INDICATORS
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
    result = list(prices[:n])
    for i in range(n, len(prices)):
        direction  = abs(prices[i] - prices[i - n])
        volatility = sum(abs(prices[j] - prices[j-1]) for j in range(i - n + 1, i + 1))
        er  = direction / volatility if volatility > 0 else 0
        sc  = (er * (fast_sc - slow_sc) + slow_sc) ** 2
        result.append(result[-1] + sc * (prices[i] - result[-1]))
    return result

def calc_er(prices, n=10):
    if len(prices) < n + 1:
        return 0.0
    direction  = abs(prices[-1] - prices[-n-1])
    volatility = sum(abs(prices[i] - prices[i-1]) for i in range(-n, 0))
    return round(direction / volatility if volatility > 0 else 0.0, 4)

def calc_ao_baffetti(high, low):
    mid = [(h + l) / 2 for h, l in zip(high, low)]
    if len(mid) < 34:
        return 0.0, 0
    series = []
    for i in range(33, len(mid)):
        series.append(sum(mid[i-4:i+1]) / 5 - sum(mid[i-33:i+1]) / 34)
    baff = 0
    for i in range(len(series) - 1, 0, -1):
        if series[i] > series[i - 1]:
            baff += 1
        else:
            break
    return round(series[-1], 6), baff

def calc_rsi(prices, n=14):
    if len(prices) < n + 1:
        return 50.0
    d = [prices[i] - prices[i-1] for i in range(1, len(prices))]
    g = [max(x, 0) for x in d]
    l = [max(-x, 0) for x in d]
    ag, al = sum(g[:n]) / n, sum(l[:n]) / n
    for i in range(n, len(g)):
        ag = (ag * (n-1) + g[i]) / n
        al = (al * (n-1) + l[i]) / n
    rs = ag / al if al > 0 else 100
    return round(100 - 100 / (1 + rs), 1)

def calc_atr(high, low, close, n=14):
    if len(close) < 2:
        return 0.0
    tr = [max(high[i] - low[i], abs(high[i] - close[i-1]), abs(low[i] - close[i-1]))
          for i in range(1, len(close))]
    if not tr:
        return 0.0
    av = sum(tr[:n]) / min(n, len(tr))
    for i in range(min(n, len(tr)), len(tr)):
        av = (av * (n-1) + tr[i]) / n
    return round(av, 5)

def calc_parabolic_sar(high, low, af0=0.02, af_max=0.2):
    if len(high) < 5:
        return low[-1], True
    sar, ep, af, bull = low[0], high[0], af0, True
    sars = [sar]
    for i in range(1, len(high)):
        prev = sars[-1]
        if bull:
            new = prev + af * (ep - prev)
            cands = low[max(0, i-2):i]
            new = min(new, min(cands)) if cands else new
            if low[i] < new:
                bull, new, ep, af = False, ep, low[i], af0
            else:
                if high[i] > ep:
                    ep = high[i]
                    af = min(af + af0, af_max)
        else:
            new = prev + af * (ep - prev)
            cands = high[max(0, i-2):i]
            new = max(new, max(cands)) if cands else new
            if high[i] > new:
                bull, new, ep, af = True, ep, high[i], af0
            else:
                if low[i] < ep:
                    ep = low[i]
                    af = min(af + af0, af_max)
        sars.append(new)
    return round(sars[-1], 5), bull

def calc_supertrend(high, low, close, period=10, mult=3.0):
    if len(close) < period + 2:
        return close[-1], True
    tr = [max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1]))
          for i in range(1, len(close))]
    atr_arr = [sum(tr[:period]) / period]
    for i in range(period, len(tr)):
        atr_arr.append((atr_arr[-1] * (period-1) + tr[i]) / period)
    pad = len(close) - len(atr_arr) - 1
    atr_full = [atr_arr[0]] * (pad + 1) + atr_arr
    hl2 = [(h + l) / 2 for h, l in zip(high, low)]
    upper = [hl2[i] + mult * atr_full[i] for i in range(len(close))]
    lower = [hl2[i] - mult * atr_full[i] for i in range(len(close))]
    st = [lower[0]]
    dir_ = [1]
    for i in range(1, len(close)):
        prev_st = st[-1]
        if close[i] > prev_st:
            new_st = max(lower[i], prev_st) if dir_[-1] == 1 else lower[i]
            dir_.append(1)
        else:
            new_st = min(upper[i], prev_st) if dir_[-1] == -1 else upper[i]
            dir_.append(-1)
        st.append(new_st)
    return round(st[-1], 5), dir_[-1] == 1

def trendycator(close):
    if len(close) < 55:
        return "GRIGIO"
    e21 = ema(close, 21)
    e55 = ema(close, 55)
    if close[-1] > e21[-1] > e55[-1]:
        return "VERDE"
    if close[-1] < e21[-1] < e55[-1]:
        return "ROSSO"
    return "GRIGIO"

def mm_align(close):
    if len(close) < 200:
        return False
    mm20  = sum(close[-20:]) / 20
    mm50  = sum(close[-50:]) / 50
    mm200 = sum(close[-200:]) / 200
    return close[-1] > mm20 > mm50 > mm200

def calc_vortex(high, low, close, n=14):
    """Vortex Index — VI+ and VI-"""
    if len(close) < n + 1:
        return 1.0, 1.0, False
    vm_plus  = [abs(high[i] - low[i-1]) for i in range(1, len(close))]
    vm_minus = [abs(low[i]  - high[i-1]) for i in range(1, len(close))]
    tr       = [max(high[i]-low[i], abs(high[i]-close[i-1]), abs(low[i]-close[i-1]))
                for i in range(1, len(close))]
    vi_plus  = round(sum(vm_plus[-n:])  / sum(tr[-n:]) if sum(tr[-n:]) > 0 else 1.0, 4)
    vi_minus = round(sum(vm_minus[-n:]) / sum(tr[-n:]) if sum(tr[-n:]) > 0 else 1.0, 4)
    bull = vi_plus > vi_minus
    return vi_plus, vi_minus, bull

def calc_rvi(close, open_, high, low, n=10):
    """Relative Vigor Index — RVI and Signal line"""
    if len(close) < n + 4:
        return 0.0, 0.0, False
    # Numerator: weighted avg of (Close - Open)
    # Denominator: weighted avg of (High - Low)
    num, den = [], []
    for i in range(3, len(close)):
        n_val = (close[i]-open_[i] + 2*(close[i-1]-open_[i-1])
                 + 2*(close[i-2]-open_[i-2]) + (close[i-3]-open_[i-3])) / 6
        d_val = (high[i]-low[i] + 2*(high[i-1]-low[i-1])
                 + 2*(high[i-2]-low[i-2]) + (high[i-3]-low[i-3])) / 6
        num.append(n_val)
        den.append(d_val)
    if len(num) < n:
        return 0.0, 0.0, False
    rvi_series = []
    for i in range(n-1, len(num)):
        d_sum = sum(den[i-n+1:i+1])
        rvi_series.append(sum(num[i-n+1:i+1]) / d_sum if d_sum != 0 else 0)
    if len(rvi_series) < 4:
        return 0.0, 0.0, False
    # Signal line: 4-bar symmetric weighted average
    sig_series = []
    for i in range(3, len(rvi_series)):
        sig_series.append((rvi_series[i] + 2*rvi_series[i-1]
                           + 2*rvi_series[i-2] + rvi_series[i-3]) / 6)
    if not sig_series:
        return 0.0, 0.0, False
    rvi_val = round(rvi_series[-1], 6)
    sig_val = round(sig_series[-1], 6)
    bull = rvi_val > sig_val
    return rvi_val, sig_val, bull

# ─────────────────────────────────────────────────────────────────────────────
# SCORING & SIGNALS — Opzione C (graduated) + Opzione D (Vortex + RVI)
# ─────────────────────────────────────────────────────────────────────────────

def calc_score(er, baff, k_pct, p7, p30, mm_ok, ao_pos, cross, trend,
               vortex_bull=False, rvi_bull=False):
    # Scala 0-75 reale (max teorico assoluto ~82)
    # ER(1)*18=18 + Baff(5)*2=10 + K%(5)*1=5 + P7(5)*2=10
    # + P30(10)*0.5=5 + MM=4 + AO=3 + Cross=8 + Vortex=2 + RVI=2 = 67
    s = (er * 18
         + min(baff, 5) * 2
         + min(abs(k_pct), 5) * 1
         + max(-5, min(5, p7)) * 2
         + max(-10, min(10, p30)) * 0.5
         + (4 if mm_ok else 0)
         + (3 if ao_pos else 0)
         + (8 if cross <= 3 else 5 if cross <= 10 else 2 if cross <= 20 else 0))
    # Vortex + RVI — bonus/malus moderato
    if vortex_bull:
        s += 2
    if rvi_bull:
        s += 2
    if not vortex_bull and not rvi_bull:
        s -= 4
    if trend == "ROSSO":
        s *= 0.6
    return round(max(0, min(75, s)), 1)

def count_conditions(price, kama_v, er, baff, trend, sar_bull, st_bull,
                     mm_ok, ao_pos, vortex_bull, rvi_bull):
    """Count how many of the 9 conditions are met (base 7 + Vortex + RVI)"""
    conds = [
        price > kama_v,           # 1. Prezzo sopra KAMA
        trend == "VERDE",         # 2. Trendycator verde
        er >= 0.40,               # 3. ER
        baff >= 3,                # 4. Baffetti
        sar_bull,                 # 5. SAR bullish
        st_bull,                  # 6. Supertrend bullish
        mm_ok or ao_pos,          # 7. MM align OR AO positivo
        vortex_bull,              # 8. Vortex bullish
        rvi_bull,                 # 9. RVI bullish
    ]
    return sum(conds)

def calc_signal(price, kama_v, er, baff, trend, ao, mm_ok,
                vortex_bull, rvi_bull, sar_bull, st_bull):
    """Opzione C — graduated signal levels"""
    if price < kama_v and trend == "ROSSO":
        return "STOP"
    if price < kama_v:
        return "USCITA"
    if ao <= 0 and trend == "GRIGIO":
        return "ATTENZIONE"
    n = count_conditions(price, kama_v, er, baff, trend,
                         sar_bull, st_bull, mm_ok, ao > 0,
                         vortex_bull, rvi_bull)
    if n >= 7:
        return "LONG_FORTE"
    if n >= 5:
        return "LONG"
    if n >= 4:
        return "EARLY_FORTE"
    if n >= 3:
        return "EARLY"
    if n >= 1:
        return "WATCH"
    return "ATTENZIONE"

def qualifies(signal, score, price, kama_v):
    """Opzione C — entry qualifies at different score thresholds by signal"""
    if price <= kama_v:
        return False
    thresholds = {
        "LONG_FORTE":  42,
        "LONG":        37,
        "EARLY_FORTE": 33,
        "EARLY":       28,
        "WATCH":       45,
    }
    min_score = thresholds.get(signal, 999)
    return score >= min_score

# ─────────────────────────────────────────────────────────────────────────────
# DATA FETCHING & ANALYSIS
# ─────────────────────────────────────────────────────────────────────────────

def analyze(ticker, name):
    try:
        df = yf.download(ticker, period="1y", interval="1d",
                         progress=False, auto_adjust=True)
        if df is None or df.empty:
            return None
        if isinstance(df.columns, pd.MultiIndex):
            df.columns = df.columns.get_level_values(0)
        df = df.loc[:, ~df.columns.duplicated()]
        df = df.dropna(subset=['Close', 'High', 'Low'])
        if len(df) < 55:
            return None

        close  = [float(x) for x in df['Close'].tolist()]
        high   = [float(x) for x in df['High'].tolist()]
        low    = [float(x) for x in df['Low'].tolist()]
        # Open needed for RVI
        open_  = [float(x) for x in df['Open'].tolist()] if 'Open' in df.columns else close[:]

        price   = close[-1]
        kama_s  = kama(close)
        kama_v  = kama_s[-1]
        k_pct   = round((price / kama_v - 1) * 100 if kama_v else 0, 2)
        er      = calc_er(close)
        ao, baff = calc_ao_baffetti(high, low)
        rsi_v   = calc_rsi(close)
        atr_v   = calc_atr(high, low, close)
        trail   = round(price - 2 * atr_v, 3)
        trend   = trendycator(close)
        mm_ok   = mm_align(close)
        sar_v, sar_bull = calc_parabolic_sar(high, low)
        st_v, st_bull   = calc_supertrend(high, low, close)
        vi_plus, vi_minus, vortex_bull = calc_vortex(high, low, close)
        rvi_val, rvi_sig, rvi_bull     = calc_rvi(close, open_, high, low)
        p7  = round((price / close[-8]  - 1) * 100 if len(close) >= 8  else 0, 2)
        p30 = round((price / close[-31] - 1) * 100 if len(close) >= 31 else 0, 2)

        cross = 0
        for i in range(len(kama_s)-1, 0, -1):
            if (close[i] > kama_s[i]) == (close[-1] > kama_v):
                cross += 1
            else:
                break

        score  = calc_score(er, baff, k_pct, p7, p30, mm_ok, ao > 0, cross, trend,
                            vortex_bull, rvi_bull)
        signal = calc_signal(price, kama_v, er, baff, trend, ao, mm_ok,
                             vortex_bull, rvi_bull, sar_bull, st_bull)
        q      = qualifies(signal, score, price, kama_v)

        return {
            "ticker": ticker, "name": name,
            "price": round(price, 3), "kama": round(kama_v, 3), "k_pct": k_pct,
            "er": er, "ao": ao, "baffetti": baff, "rsi": rsi_v,
            "atr": atr_v, "trailing_stop": trail,
            "trend": trend, "mm_aligned": mm_ok,
            "sar": sar_v, "sar_bullish": sar_bull,
            "supertrend": st_v, "supertrend_bullish": st_bull,
            "vi_plus": vi_plus, "vi_minus": vi_minus, "vortex_bullish": vortex_bull,
            "rvi": rvi_val, "rvi_signal": rvi_sig, "rvi_bullish": rvi_bull,
            "perf7": p7, "perf30": p30,
            "score": score, "signal": signal, "qualifies": q,
        }
    except Exception as e:
        print(f"  ✗ {ticker}: {e}")
        return None

# ─────────────────────────────────────────────────────────────────────────────
# PORTFOLIO MANAGEMENT
# ─────────────────────────────────────────────────────────────────────────────

STATE_FILE = "portfolio_state.json"

def load_state():
    if os.path.exists(STATE_FILE):
        with open(STATE_FILE) as f:
            return json.load(f)
    return {"paesi": {"positions": []}, "new_area": {"positions": []}}

def save_state(state):
    with open(STATE_FILE, "w") as f:
        json.dump(state, f, indent=2, default=str)

def update_portfolio(existing, candidates, today_str):
    today  = date.fromisoformat(today_str)
    kept   = []
    exited = []

    for pos in existing:
        cur = next((c for c in candidates if c["ticker"] == pos["ticker"]), None)
        if cur is None:
            pos["warning"] = "Dati non disponibili"
            kept.append(pos)
            continue

        entry_date = date.fromisoformat(pos["entry_date"])
        days_held  = (today - entry_date).days
        cur_gain   = round((cur["price"] / pos["entry_price"] - 1) * 100, 2)
        new_trail  = round(cur["price"] - 2 * cur["atr"], 3)
        trail_stop = max(pos.get("trailing_stop", new_trail), new_trail)

        exit_reason = None
        if cur["k_pct"] < 0:
            exit_reason = "K% negativo — prezzo sotto KAMA"
        elif cur["price"] <= trail_stop:
            exit_reason = "Trailing Stop colpito"
        elif cur["score"] < 20:
            exit_reason = "Score < 20"
        elif days_held >= 10:
            exit_reason = f"Time Stop — {days_held} giorni"

        if exit_reason:
            exited.append({**pos, "exit_reason": exit_reason,
                           "exit_price": cur["price"], "final_gain_pct": cur_gain})
            continue

        pre_alert  = days_held >= 7 and cur_gain < 5.0
        target_hit = cur_gain >= 5.0

        pos.update({
            "current_price": cur["price"], "current_gain_pct": cur_gain,
            "days_held": days_held, "trailing_stop": trail_stop,
            "pre_alert": pre_alert, "target_hit": target_hit,
            "signal": cur["signal"], "score": cur["score"],
            "er": cur["er"], "trend": cur["trend"],
            "supertrend_bullish": cur["supertrend_bullish"],
            "sar_bullish": cur["sar_bullish"],
            "vortex_bullish": cur.get("vortex_bullish", False),
            "rvi_bullish": cur.get("rvi_bullish", False),
            "perf7": cur["perf7"], "perf30": cur["perf30"],
            "warning": None,
        })
        kept.append(pos)

    # Fill empty slots — ranked by ER desc
    slots = MAX_POSITIONS - len(kept)
    existing_tickers = {p["ticker"] for p in kept}
    new_q = sorted(
        [c for c in candidates if c["qualifies"] and c["ticker"] not in existing_tickers],
        key=lambda x: x["er"], reverse=True
    )

    for c in new_q[:slots]:
        entry_p = c["price"]
        stop    = round(max(entry_p - 2 * c["atr"], c["trailing_stop"]), 3)
        kept.append({
            "ticker": c["ticker"], "name": c["name"],
            "entry_date": today_str, "entry_price": entry_p,
            "current_price": entry_p, "target_price": round(entry_p * 1.05, 3),
            "stop_loss": stop, "trailing_stop": stop,
            "current_gain_pct": 0.0, "days_held": 0,
            "pre_alert": False, "target_hit": False,
            "score": c["score"], "er": c["er"], "signal": c["signal"],
            "trend": c["trend"],
            "supertrend_bullish": c["supertrend_bullish"],
            "sar_bullish": c["sar_bullish"],
            "vortex_bullish": c.get("vortex_bullish", False),
            "rvi_bullish": c.get("rvi_bullish", False),
            "perf7": c["perf7"], "perf30": c["perf30"],
            "warning": None,
        })

    # Weights by Score
    total_score = sum(p["score"] for p in kept)
    for p in kept:
        p["weight_pct"] = round(p["score"] / total_score * 100, 1) if total_score else 0

    return kept, exited

# ─────────────────────────────────────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────────────────────────────────────

def main():
    now       = datetime.now(ROME_TZ)
    today_str = now.date().isoformat()
    print(f"🦅 RAPTOR GEOGRAFIA v4 — {now.strftime('%d/%m/%Y %H:%M')} CET")
    print(f"   Max posizioni: {MAX_POSITIONS} | Vortex + RVI attivi")

    state = load_state()

    print("\n📊 PAESI...")
    paesi_data = []
    for t, n in PAESI.items():
        print(f"  {t}...", end=" ", flush=True)
        r = analyze(t, n)
        if r:
            paesi_data.append(r)
            print(f"✓ score={r['score']} signal={r['signal']} V={'✅' if r['vortex_bullish'] else '❌'} RVI={'✅' if r['rvi_bullish'] else '❌'}")
        else:
            print("✗")

    print("\n📊 NEW AREA...")
    new_area_data = []
    for t, n in NEW_AREA.items():
        print(f"  {t}...", end=" ", flush=True)
        r = analyze(t, n)
        if r:
            new_area_data.append(r)
            print(f"✓ score={r['score']} signal={r['signal']} V={'✅' if r['vortex_bullish'] else '❌'} RVI={'✅' if r['rvi_bullish'] else '❌'}")
        else:
            print("✗")

    print("\n💰 XEON...")
    xeon = analyze(XEON_TICKER, "Xtrackers EUR Overnight Rate Swap UCITS ETF")

    # Update portfolios
    paesi_pos, paesi_exited = update_portfolio(
        state["paesi"].get("positions", []), paesi_data, today_str)
    new_area_pos, new_area_exited = update_portfolio(
        state["new_area"].get("positions", []), new_area_data, today_str)

    state["paesi"]["positions"]    = paesi_pos
    state["new_area"]["positions"] = new_area_pos
    state["paesi"].setdefault("history", []).extend(paesi_exited)
    state["new_area"].setdefault("history", []).extend(new_area_exited)
    save_state(state)

    def top10(data):
        return sorted(data, key=lambda x: x["score"], reverse=True)[:10]

    output = {
        "updated_at":      now.isoformat(),
        "updated_display": now.strftime("%d/%m/%Y %H:%M CET"),
        "paesi": {
            "positions":  paesi_pos,
            "use_xeon":   len(paesi_pos) == 0,
            "xeon_price": xeon["price"] if xeon else None,
            "watchlist":  top10([d for d in paesi_data if not d["qualifies"]]),
            "qualified":  [d for d in paesi_data if d["qualifies"]],
            "all":        sorted(paesi_data, key=lambda x: x["score"], reverse=True),
        },
        "new_area": {
            "positions":  new_area_pos,
            "use_xeon":   len(new_area_pos) == 0,
            "xeon_price": xeon["price"] if xeon else None,
            "watchlist":  top10([d for d in new_area_data if not d["qualifies"]]),
            "qualified":  [d for d in new_area_data if d["qualifies"]],
            "all":        sorted(new_area_data, key=lambda x: x["score"], reverse=True),
        },
        "xeon": xeon,
    }

    with open("geografia.json", "w") as f:
        json.dump(output, f, indent=2, default=str)

    print(f"\n✅ geografia.json aggiornato — {now.strftime('%d/%m/%Y %H:%M CET')}")
    print(f"   PAESI   : {len(paesi_pos)} posizioni {'| XEON 100%' if not paesi_pos else ''}")
    print(f"   NEW AREA: {len(new_area_pos)} posizioni {'| XEON 100%' if not new_area_pos else ''}")

if __name__ == "__main__":
    main()
