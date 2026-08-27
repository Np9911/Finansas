#!/usr/bin/env python3
"""
Screener y backtester de una estrategia de reversión a la media basada en RSI diario.

Uso:
    python rsi_screener.py --tickers AAPL MSFT GOOGL AMZN NVDA META --period 2y
    python rsi_screener.py --csv-dir ./mis_datos --period 2y
    python rsi_screener.py --demo

Ver RSI_STRATEGY.md para las reglas completas de la estrategia.

Fuente de datos: intenta descargar precios diarios con yfinance. Si no hay acceso
a internet (por ejemplo, dentro de un entorno sandboxed), usa --csv-dir para
apuntar a un directorio con un CSV por ticker (columnas: date,open,high,low,close,volume)
o --demo para generar datos sintéticos de ejemplo y ver el flujo completo funcionando.
"""

import argparse
import sys
import zlib
from dataclasses import dataclass, field

import numpy as np
import pandas as pd

RSI_PERIOD = 14
OVERSOLD = 30
OVERBOUGHT = 70
TREND_SMA = 200
STOP_LOSS_PCT = 0.08
MAX_HOLD_DAYS = 60


# --------------------------------------------------------------------------
# Datos
# --------------------------------------------------------------------------

def fetch_yfinance(ticker, period):
    import yfinance as yf
    df = yf.download(ticker, period=period, interval="1d", progress=False, auto_adjust=True)
    if df.empty:
        raise ValueError(f"Sin datos para {ticker}")
    if isinstance(df.columns, pd.MultiIndex):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)[["open", "high", "low", "close", "volume"]]
    df.index.name = "date"
    return df


def load_csv(path):
    df = pd.read_csv(path, parse_dates=["date"]).set_index("date").sort_index()
    return df[["open", "high", "low", "close", "volume"]]


def make_demo_series(ticker, seed, days=750, regime="mixed"):
    """Genera una serie sintética de precios con tramos alcistas/bajistas
    alternados (para producir oscilaciones de RSI realistas) únicamente para
    demostrar el flujo del screener cuando no hay acceso a datos de mercado
    reales."""
    rng = np.random.default_rng(seed)
    long_drift = {"alcista": 0.00045, "bajista": -0.00025, "mixed": 0.00015}[regime]

    rets = np.zeros(days)
    t, sign = 0, 1
    while t < days:
        phase_len = min(int(rng.integers(10, 26)), days - t)
        local_drift = sign * rng.uniform(0.004, 0.008)
        rets[t:t + phase_len] = rng.normal(local_drift, 0.01, phase_len)
        t += phase_len
        sign *= -1
    rets += long_drift

    close = 100 * np.exp(np.cumsum(rets))
    high = close * (1 + np.abs(rng.normal(0, 0.006, days)))
    low = close * (1 - np.abs(rng.normal(0, 0.006, days)))
    open_ = close * (1 + rng.normal(0, 0.004, days))
    volume = rng.integers(1_000_000, 8_000_000, days)
    idx = pd.bdate_range(end=pd.Timestamp.today().normalize(), periods=days)
    return pd.DataFrame(
        {"open": open_, "high": high, "low": low, "close": close, "volume": volume},
        index=idx,
    )


# --------------------------------------------------------------------------
# Indicadores
# --------------------------------------------------------------------------

def compute_rsi(close, period=RSI_PERIOD):
    delta = close.diff()
    gain = delta.clip(lower=0)
    loss = -delta.clip(upper=0)
    avg_gain = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0, np.nan)
    rsi = 100 - 100 / (1 + rs)
    return rsi.fillna(50)


def prepare(df):
    df = df.copy()
    df["rsi"] = compute_rsi(df["close"])
    df["sma200"] = df["close"].rolling(TREND_SMA, min_periods=max(20, TREND_SMA // 4)).mean()
    df["uptrend"] = df["close"] > df["sma200"]
    return df


# --------------------------------------------------------------------------
# Backtest: reversión a la media por cruce de RSI 30 / 70
# --------------------------------------------------------------------------

@dataclass
class Trade:
    entry_date: pd.Timestamp
    entry_price: float
    exit_date: pd.Timestamp = None
    exit_price: float = None
    reason: str = None

    @property
    def return_pct(self):
        return (self.exit_price / self.entry_price - 1) * 100


@dataclass
class BacktestResult:
    ticker: str
    trades: list = field(default_factory=list)

    @property
    def n(self):
        return len(self.trades)

    @property
    def win_rate(self):
        if not self.trades:
            return 0.0
        wins = sum(1 for t in self.trades if t.return_pct > 0)
        return wins / self.n * 100

    @property
    def avg_return(self):
        if not self.trades:
            return 0.0
        return sum(t.return_pct for t in self.trades) / self.n

    @property
    def profit_factor(self):
        gains = sum(t.return_pct for t in self.trades if t.return_pct > 0)
        losses = -sum(t.return_pct for t in self.trades if t.return_pct < 0)
        if losses == 0:
            return float("inf") if gains > 0 else 0.0
        return gains / losses

    @property
    def compounded_return_pct(self):
        equity = 1.0
        for t in self.trades:
            equity *= (1 + t.return_pct / 100)
        return (equity - 1) * 100


def backtest(df, require_uptrend=True, stop_loss_pct=STOP_LOSS_PCT, max_hold_days=MAX_HOLD_DAYS):
    trades = []
    in_position = False
    entry = None
    entry_idx = None
    dates = df.index
    rsi = df["rsi"].values
    close = df["close"].values
    uptrend = df["uptrend"].values

    for i in range(1, len(df)):
        if not in_position:
            crossed_up = rsi[i - 1] < OVERSOLD <= rsi[i]
            trend_ok = uptrend[i] if require_uptrend else True
            if crossed_up and trend_ok and not np.isnan(close[i]):
                in_position = True
                entry = Trade(entry_date=dates[i], entry_price=close[i])
                entry_idx = i
        else:
            held_days = i - entry_idx
            stop_hit = close[i] <= entry.entry_price * (1 - stop_loss_pct)
            crossed_down = rsi[i - 1] > OVERBOUGHT >= rsi[i]
            time_exit = held_days >= max_hold_days

            if stop_hit or crossed_down or time_exit:
                entry.exit_date = dates[i]
                entry.exit_price = close[i]
                entry.reason = "stop_loss" if stop_hit else ("take_profit" if crossed_down else "tiempo_max")
                trades.append(entry)
                in_position = False
                entry = None

    return BacktestResult(ticker="", trades=trades)


# --------------------------------------------------------------------------
# Screener diario: estado y señal de cada ticker "hoy"
# --------------------------------------------------------------------------

def screen_today(df):
    last = df.iloc[-1]
    prev = df.iloc[-2]
    rsi_today = last["rsi"]

    if rsi_today < OVERSOLD:
        estado = "Sobreventa"
    elif rsi_today > OVERBOUGHT:
        estado = "Sobrecompra"
    else:
        estado = "Neutral"

    crossed_up = prev["rsi"] < OVERSOLD <= last["rsi"]
    crossed_down = prev["rsi"] > OVERBOUGHT >= last["rsi"]

    if crossed_up and last["uptrend"]:
        senal = "COMPRA"
    elif crossed_up and not last["uptrend"]:
        senal = "COMPRA (sin filtro de tendencia)"
    elif crossed_down:
        senal = "VENTA / TOMA DE GANANCIA"
    elif rsi_today < OVERSOLD + 5:
        senal = "VIGILAR (acercándose a sobreventa)"
    else:
        senal = "ESPERAR"

    return {
        "rsi": round(float(rsi_today), 1),
        "estado": estado,
        "tendencia": "Alcista (>SMA200)" if bool(last["uptrend"]) else "Bajista/lateral (<SMA200)",
        "senal": senal,
        "precio": round(float(last["close"]), 2),
    }


# --------------------------------------------------------------------------
# Orquestación
# --------------------------------------------------------------------------

def run(tickers, source, period, csv_dir, demo):
    rows = []
    for i, ticker in enumerate(tickers):
        try:
            if demo:
                regime = ["alcista", "bajista", "mixed"][i % 3]
                seed = zlib.crc32(ticker.encode())
                raw = make_demo_series(ticker, seed=seed, regime=regime)
            elif csv_dir:
                raw = load_csv(f"{csv_dir}/{ticker}.csv")
            else:
                raw = fetch_yfinance(ticker, period)
        except Exception as e:
            print(f"[!] {ticker}: no se pudo obtener datos ({e})", file=sys.stderr)
            continue

        if len(raw) < RSI_PERIOD + 5:
            print(f"[!] {ticker}: histórico insuficiente", file=sys.stderr)
            continue

        df = prepare(raw)
        bt = backtest(df)
        bt.ticker = ticker
        today = screen_today(df)

        rows.append({
            "ticker": ticker,
            **today,
            "operaciones_historicas": bt.n,
            "win_rate_%": round(bt.win_rate, 1),
            "retorno_prom_%": round(bt.avg_return, 2),
            "profit_factor": round(bt.profit_factor, 2) if bt.profit_factor != float("inf") else None,
            "retorno_compuesto_%": round(bt.compounded_return_pct, 1),
        })

    if not rows:
        print("No se obtuvieron datos para ningún ticker.", file=sys.stderr)
        sys.exit(1)

    result = pd.DataFrame(rows)

    def score(row):
        if "COMPRA" not in str(row["senal"]):
            return -1_000 + row["win_rate_%"]  # las que no tienen señal de compra van al final, ordenadas igual por calidad
        return row["win_rate_%"] * 0.6 + min(row["retorno_prom_%"], 20) * 2

    result["score"] = result.apply(score, axis=1)
    result = result.sort_values("score", ascending=False).drop(columns="score").reset_index(drop=True)
    result.index = result.index + 1
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--tickers", nargs="+", default=[
        "SPY", "QQQ", "AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "XLE", "XLF",
    ])
    parser.add_argument("--period", default="2y", help="Historial a descargar (ej. 1y, 2y, 5y)")
    parser.add_argument("--csv-dir", default=None, help="Directorio con un CSV por ticker en vez de descargar")
    parser.add_argument("--demo", action="store_true", help="Usa datos sintéticos de demostración (sin red)")
    parser.add_argument("--out", default=None, help="Ruta CSV de salida (opcional)")
    args = parser.parse_args()

    result = run(args.tickers, source="yfinance", period=args.period, csv_dir=args.csv_dir, demo=args.demo)

    with pd.option_context("display.width", 160, "display.max_columns", None):
        print(result.to_string())

    if args.out:
        result.to_csv(args.out)
        print(f"\nGuardado en {args.out}")


if __name__ == "__main__":
    main()
