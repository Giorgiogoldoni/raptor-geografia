# 🦅 RAPTOR GEOGRAFIA

Portfolio manager autonomo per ETF UCITS quotati in Europa.
Due portafogli separati: **PAESI** + **NEW AREA**.

## 📐 Regole operative

### ENTRATA (tutte e 7 soddisfatte)
| # | Condizione | Soglia |
|---|---|---|
| 1 | Segnale RAPTOR | LONG / EARLY / WATCH |
| 2 | Score | ≥ 40 |
| 3 | Trendycator | 🟢 VERDE |
| 4 | ER (Efficiency Ratio) | ≥ 0.50 |
| 5 | AO + Baffetti | ≥ 3 barre consecutive |
| 6 | Parabolic SAR | Bullish (prezzo > SAR) |
| 7 | Supertrend | Bullish |

- **Conferma**: a chiusura di sessione
- **Giorno preferito**: Mercoledì
- **Ranking**: per ER decrescente
- **Pesi**: proporzionali allo Score

### USCITA (basta 1)
| Condizione | Tipo |
|---|---|
| K% negativo (prezzo sotto KAMA) | Immediata |
| Trailing Stop colpito (Prezzo − 2×ATR) | Immediata |
| Score < 20 | Immediata |
| Supertrend gira rosso | Pre-allerta |
| Giorno 7 e gain < +5% | Pre-allerta |
| Giorno 10 | Time stop obbligatorio |

### Obiettivo per operazione
- **Target**: +5% dal prezzo di ingresso
- **Stop Loss**: MAX(Trailing Stop, Entry − 2×ATR)

### Cuscinetto
- **XEON** (Xtrackers EUR Overnight Rate) quando nessun ETF qualifica
- Allocazione XEON: 100% se 0 posizioni

## 🔄 Aggiornamento automatico

GitHub Actions esegue `raptor_geografia.py` ogni ora dalle 09:00 alle 19:00 CET (Lun–Ven).

## 🚀 Setup

```bash
git clone https://github.com/TUO_USERNAME/raptor-geografia
cd raptor-geografia
pip install -r requirements.txt
python raptor_geografia.py
python -m http.server 8080  # apri http://localhost:8080
```

## 📁 File

| File | Descrizione |
|---|---|
| `raptor_geografia.py` | Script principale — calcola indicatori, aggiorna portafogli, genera JSON |
| `index.html` | Dashboard visuale |
| `geografia.json` | Dati generati dallo script (auto-aggiornato) |
| `portfolio_state.json` | Stato portafogli persistente |
| `.github/workflows/update.yml` | GitHub Actions — aggiornamento orario |

## 📊 Indicatori calcolati

| Indicatore | Parametri |
|---|---|
| KAMA | n=10, fast=2, slow=30 |
| ER (Efficiency Ratio) | n=10 |
| AO (Awesome Oscillator) | SMA5 − SMA34 midpoint |
| Baffetti | barre AO consecutive crescenti |
| RSI | n=14 |
| Trendycator | EMA21 vs EMA55 |
| ATR | n=14 |
| Trailing Stop | Prezzo − 2×ATR |
| K% | (Prezzo/KAMA−1)×100 |
| MM Align | Prezzo > MM20 > MM50 > MM200 |
| Parabolic SAR | AF=0.02, max=0.20 |
| Supertrend | period=10, mult=3.0 |

---
🦅 RAPTOR GEOGRAFIA — *Fly High, Trade Smart*
