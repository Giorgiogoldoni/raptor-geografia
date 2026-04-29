# ═══════════════════════════════════════════════════════════════════════════════
# PATCH DA APPLICARE A raptor_geografia.py
# Aggiunge regime visivo (Hurst + ADX) senza toccare nessuna logica di segnale
#
# ISTRUZIONI:
# 1. Apri raptor_geografia.py su GitHub
# 2. Clicca ✏️ (modifica)
# 3. Applica le 3 modifiche indicate sotto
# 4. Commit → Actions → testa
# ═══════════════════════════════════════════════════════════════════════════════

# ─────────────────────────────────────────────────────────────────────────────
# MODIFICA 1 — Aggiungi queste due funzioni DOPO calc_rvi() e PRIMA di calc_score()
# Circa riga 190 del tuo file attuale
# ─────────────────────────────────────────────────────────────────────────────

def calc_hurst(prices, min_points=50):
    """
    Hurst Exponent con metodo varianza (leggero, adatto a real-time).
    Restituisce H arrotondato a 3 decimali, o 0.5 se dati insufficienti.
    H > 0.55 → trending  |  H ≈ 0.5 → random walk  |  H < 0.45 → mean reverting
    """
    if len(prices) < min_points:
        return 0.5
    import math
    lags = [2, 4, 8, 16, 32]
    lags = [l for l in lags if l < len(prices) // 2]
    if len(lags) < 3:
        return 0.5
    log_p = [math.log(p) for p in prices if p > 0]
    if len(log_p) < max(lags) + 1:
        return 0.5
    vars_ = []
    for lag in lags:
        diffs = [log_p[i] - log_p[i - lag] for i in range(lag, len(log_p))]
        if not diffs:
            return 0.5
        mean_d = sum(diffs) / len(diffs)
        var = sum((d - mean_d) ** 2 for d in diffs) / len(diffs)
        vars_.append(var if var > 0 else 1e-10)
    log_lags = [math.log(l) for l in lags]
    log_vars = [math.log(v) for v in vars_]
    n = len(lags)
    mean_x = sum(log_lags) / n
    mean_y = sum(log_vars) / n
    num = sum((log_lags[i] - mean_x) * (log_vars[i] - mean_y) for i in range(n))
    den = sum((log_lags[i] - mean_x) ** 2 for i in range(n))
    if den == 0:
        return 0.5
    slope = num / den
    h = slope / 2.0
    return round(max(0.1, min(0.9, h)), 3)


def classify_regime(h, adx_val, pdi_val, ndi_val):
    """
    Classifica il regime in 4 stati basandosi su Hurst + ADX.
    Non influenza nessuna logica di segnale — solo visivo.

    Ritorna dict con: code, label, color, description
    """
    if h > 0.55 and adx_val > 25:
        if pdi_val >= ndi_val:
            return {
                "code":        "TREND_UP",
                "label":       "📈 Trend ↑",
                "color":       "#1D9E75",
                "description": "Serie persistente con trend rialzista confermato da ADX"
            }
        else:
            return {
                "code":        "TREND_DOWN",
                "label":       "📉 Trend ↓",
                "color":       "#E24B4A",
                "description": "Serie persistente con trend ribassista confermato da ADX"
            }
    elif h < 0.45 and adx_val < 25:
        return {
            "code":        "MEAN_REV",
            "label":       "↔ Mean Rev",
            "color":       "#378ADD",
            "description": "Serie anti-persistente, tende a tornare alla media — mercato laterale"
        }
    elif h > 0.55 and adx_val < 20:
        return {
            "code":        "SQUEEZE",
            "label":       "◈ Squeeze",
            "color":       "#BA7517",
            "description": "Memoria alta ma ADX debole — possibile breakout imminente"
        }
    else:
        return {
            "code":        "UNCERTAIN",
            "label":       "~ Incerto",
            "color":       "#888780",
            "description": "Segnali contrastanti tra Hurst e ADX — regime non classificabile"
        }


# ─────────────────────────────────────────────────────────────────────────────
# MODIFICA 2 — Nella funzione analyze(), aggiungi DOPO il calcolo di calc_rvi
# e PRIMA del calcolo di score (cerca "score = calc_score(")
#
# Aggiungi queste righe:
# ─────────────────────────────────────────────────────────────────────────────

    # ── Regime di mercato (solo visivo) ──────────────────────────────────────
    hurst_val = calc_hurst(close)

    # ADX semplificato su finestra 14 (inline, non serve funzione separata)
    _adx_n = 14
    _adx_val, _pdi_val, _ndi_val = 20.0, 25.0, 20.0   # default neutri
    if len(close) >= _adx_n + 2:
        _tr, _pdm, _ndm = [], [], []
        for _i in range(1, len(close)):
            _tr.append(max(
                high[_i] - low[_i],
                abs(high[_i] - close[_i-1]),
                abs(low[_i] - close[_i-1])
            ))
            _up = high[_i] - high[_i-1]
            _dn = low[_i-1] - low[_i]
            _pdm.append(_up if _up > _dn and _up > 0 else 0.0)
            _ndm.append(_dn if _dn > _up and _dn > 0 else 0.0)
        def _ema14(vals):
            k = 2 / (_adx_n + 1)
            r = [vals[0]]
            for v in vals[1:]:
                r.append(v * k + r[-1] * (1 - k))
            return r
        _atr14 = _ema14(_tr)
        _pdi14 = [100 * p / (a + 1e-10) for p, a in zip(_ema14(_pdm), _atr14)]
        _ndi14 = [100 * n / (a + 1e-10) for n, a in zip(_ema14(_ndm), _atr14)]
        _dx    = [100 * abs(p - n) / (p + n + 1e-10) for p, n in zip(_pdi14, _ndi14)]
        _adx14 = _ema14(_dx)
        _adx_val = round(float(_adx14[-1]), 1)
        _pdi_val = round(float(_pdi14[-1]), 1)
        _ndi_val = round(float(_ndi14[-1]), 1)

    regime = classify_regime(hurst_val, _adx_val, _pdi_val, _ndi_val)
    # ── Fine regime ──────────────────────────────────────────────────────────


# ─────────────────────────────────────────────────────────────────────────────
# MODIFICA 3 — Nel dict result{} di analyze(), aggiungi questi campi
# Mettili DOPO "stress_score" e PRIMA di "buy_level"
# ─────────────────────────────────────────────────────────────────────────────

            "hurst":           hurst_val,
            "adx":             _adx_val,
            "regime":          regime,


# ─────────────────────────────────────────────────────────────────────────────
# ESEMPIO — Come appariranno i dati nel geografia.json per ogni ETF:
# ─────────────────────────────────────────────────────────────────────────────
#
# "hurst": 0.623,
# "adx": 31.4,
# "regime": {
#     "code":        "TREND_UP",
#     "label":       "📈 Trend ↑",
#     "color":       "#1D9E75",
#     "description": "Serie persistente con trend rialzista confermato da ADX"
# }
#
# Nell'HTML puoi usarlo così:
#   const regime = etf.regime;
#   badge.style.color = regime.color;
#   badge.textContent = regime.label;
#   tooltip.textContent = `H=${etf.hurst} · ADX=${etf.adx} · ${regime.description}`;
# ─────────────────────────────────────────────────────────────────────────────
