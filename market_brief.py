#!/usr/bin/env python3
"""
Brief diario de mercado: resumen matutino de lo que puede mover a los índices
hoy — variación de índices/volatilidad, calendario de resultados (earnings) de
la próxima semana, titulares recientes y un recordatorio de qué eventos
macroeconómicos recurrentes caen hoy (y cuáles vigilar en el mes).

Uso:
    python market_brief.py --demo
    python market_brief.py --indices SPY QQQ DIA IWM --watchlist AAPL MSFT GOOGL AMZN NVDA META TSLA
    python market_brief.py --json-out brief.json

Fuente de datos: yfinance (precios, calendario de resultados, titulares). Si
no hay acceso a internet (por ejemplo, dentro de un entorno sandboxed), usa
--demo para generar un brief de ejemplo con datos sintéticos y ver el flujo
completo funcionando.

Este script no reemplaza un calendario económico en vivo: la sección de
eventos macro es una referencia de frecuencia/horario típico (no fechas
exactas descargadas), y debe confirmarse contra la fuente oficial
(federalreserve.gov, bls.gov) antes de operar con esa información.
"""

import argparse
import json
import sys
from datetime import datetime, timedelta

DEFAULT_INDICES = ["SPY", "QQQ", "DIA", "IWM"]
VIX_TICKER = "^VIX"
DEFAULT_WATCHLIST = ["AAPL", "MSFT", "GOOGL", "AMZN", "NVDA", "META", "TSLA", "JPM"]
DEFAULT_NEWS_TICKERS = ["SPY", "AAPL", "NVDA"]

INDEX_NAMES = {
    "SPY": "S&P 500 (SPY)",
    "QQQ": "Nasdaq 100 (QQQ)",
    "DIA": "Dow Jones (DIA)",
    "IWM": "Russell 2000 (IWM)",
    "^VIX": "Volatilidad (VIX)",
}

MACRO_REFERENCE = [
    {"evento": "Solicitudes iniciales de desempleo", "cuando": "Todos los jueves, ~8:30am ET", "fuente": "Dept. of Labor", "impacto": "Medio"},
    {"evento": "Reporte de empleo (Nonfarm Payrolls)", "cuando": "Primer viernes del mes (típico), ~8:30am ET", "fuente": "BLS", "impacto": "Alto"},
    {"evento": "Inflación al consumidor (CPI)", "cuando": "Entre el día 10 y 15 del mes (varía)", "fuente": "BLS", "impacto": "Alto"},
    {"evento": "Inflación PCE (indicador preferido de la Fed)", "cuando": "Última semana del mes (varía)", "fuente": "BEA", "impacto": "Alto"},
    {"evento": "Decisión de tasas (FOMC)", "cuando": "8 reuniones al año, ~cada 6 semanas, miércoles", "fuente": "Federal Reserve", "impacto": "Muy alto"},
    {"evento": "Ventas minoristas (Retail Sales)", "cuando": "A mediados de mes (varía)", "fuente": "Census Bureau", "impacto": "Medio"},
    {"evento": "ISM Manufacturing / Services PMI", "cuando": "Primeros días hábiles del mes", "fuente": "ISM", "impacto": "Medio"},
]


# --------------------------------------------------------------------------
# Datos en vivo (yfinance)
# --------------------------------------------------------------------------

def fetch_change(ticker):
    """Último cierre y variación % vs. el cierre previo, usando 5 días de historial."""
    import yfinance as yf
    df = yf.download(ticker, period="5d", interval="1d", progress=False, auto_adjust=True)
    if df.empty or len(df) < 2:
        raise ValueError(f"Sin datos suficientes para {ticker}")
    if hasattr(df.columns, "levels"):
        df.columns = df.columns.get_level_values(0)
    df = df.rename(columns=str.lower)
    closes = df["close"].dropna()
    last, prev = float(closes.iloc[-1]), float(closes.iloc[-2])
    change_pct = (last - prev) / prev * 100
    return round(last, 2), round(change_pct, 2)


def fetch_snapshot(tickers):
    out = []
    for t in tickers:
        try:
            price, change_pct = fetch_change(t)
            out.append({"ticker": t, "name": INDEX_NAMES.get(t, t), "price": price, "change_pct": change_pct})
        except Exception as exc:
            out.append({"ticker": t, "name": INDEX_NAMES.get(t, t), "error": str(exc)})
    return out


def fetch_earnings(tickers, days_ahead):
    import yfinance as yf
    today = datetime.now().date()
    window_end = today + timedelta(days=days_ahead)
    rows = []
    for t in tickers:
        try:
            dates_df = yf.Ticker(t).get_earnings_dates(limit=12)
            if dates_df is None or dates_df.empty:
                continue
            for ts in dates_df.index:
                d = ts.date()
                if today <= d <= window_end:
                    rows.append({"ticker": t, "date": d.isoformat()})
        except Exception:
            continue
    rows.sort(key=lambda r: r["date"])
    return rows


def fetch_headlines(tickers, limit_per_ticker=3, max_total=10):
    import yfinance as yf
    items = []
    seen_titles = set()
    for t in tickers:
        try:
            news = yf.Ticker(t).news or []
        except Exception:
            continue
        for raw in news[:limit_per_ticker]:
            content = raw.get("content", raw)
            title = content.get("title")
            if not title or title in seen_titles:
                continue
            seen_titles.add(title)
            publisher = (content.get("provider") or {}).get("displayName") or content.get("publisher") or ""
            link = (content.get("canonicalUrl") or {}).get("url") or content.get("link") or ""
            items.append({"ticker": t, "title": title, "publisher": publisher, "link": link})
    return items[:max_total]


# --------------------------------------------------------------------------
# Datos demo (sin red)
# --------------------------------------------------------------------------

def demo_snapshot():
    demo_values = {
        "SPY": (571.32, 0.42), "QQQ": (489.71, 0.68), "DIA": (398.05, -0.15),
        "IWM": (211.44, 1.10), "^VIX": (14.82, -3.20),
    }
    return [
        {"ticker": t, "name": INDEX_NAMES.get(t, t), "price": p, "change_pct": c}
        for t, (p, c) in demo_values.items()
    ]


def demo_earnings(days_ahead):
    today = datetime.now().date()
    offsets = [1, 2, 4, 6]
    tickers = ["NVDA", "JPM", "TSLA", "META"]
    rows = [
        {"ticker": t, "date": (today + timedelta(days=o)).isoformat()}
        for t, o in zip(tickers, offsets) if o <= days_ahead
    ]
    return rows


def demo_headlines():
    return [
        {"ticker": "SPY", "title": "La Fed mantiene sin cambios el tono sobre próximos recortes de tasas", "publisher": "Reuters (demo)", "link": ""},
        {"ticker": "NVDA", "title": "Demanda de chips de IA sigue superando expectativas del mercado", "publisher": "Bloomberg (demo)", "link": ""},
        {"ticker": "AAPL", "title": "Ventas de la nueva línea de productos superan estimados de analistas", "publisher": "CNBC (demo)", "link": ""},
    ]


# --------------------------------------------------------------------------
# Macro: solo lo que se puede derivar de forma determinista de la fecha
# --------------------------------------------------------------------------

def macro_today(today):
    items = []
    if today.weekday() == 3:  # jueves
        items.append("Hoy es jueves: se publican las Solicitudes Iniciales de Desempleo (~8:30am ET).")
    if today.weekday() == 4 and today.day <= 7:  # primer viernes del mes
        items.append("Hoy es el primer viernes del mes: suele publicarse el Reporte de Empleo (Nonfarm Payrolls) (~8:30am ET).")
    if not items:
        items.append("Sin eventos macro recurrentes deterministas para hoy. Revisa el calendario de referencia y las fuentes oficiales para publicaciones puntuales (CPI, PCE, FOMC, etc.).")
    return items


# --------------------------------------------------------------------------
# Armado del brief y salida
# --------------------------------------------------------------------------

def build_brief(args):
    today = datetime.now().date()
    if args.demo:
        snapshot = demo_snapshot()
        earnings = demo_earnings(args.earnings_days)
        headlines = demo_headlines()
        mode = "demo"
    else:
        snapshot = fetch_snapshot(args.indices + [VIX_TICKER])
        earnings = fetch_earnings(args.watchlist, args.earnings_days)
        headlines = fetch_headlines(args.news_tickers, max_total=args.top_news)
        mode = "live"

    return {
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "mode": mode,
        "indices": snapshot,
        "earnings": earnings,
        "headlines": headlines,
        "macro_today": macro_today(today),
        "macro_reference": MACRO_REFERENCE,
    }


def render_text(brief):
    lines = []
    lines.append(f"=== Brief de mercado — {brief['generated_at']} ({brief['mode']}) ===\n")

    lines.append("Índices y volatilidad:")
    for row in brief["indices"]:
        if "error" in row:
            lines.append(f"  {row['name']:<22} sin datos ({row['error']})")
            continue
        sign = "+" if row["change_pct"] >= 0 else ""
        lines.append(f"  {row['name']:<22} {row['price']:>10.2f}  {sign}{row['change_pct']:.2f}%")

    lines.append("\nEventos macro de hoy:")
    for item in brief["macro_today"]:
        lines.append(f"  - {item}")

    lines.append(f"\nResultados (earnings) en los próximos días:")
    if brief["earnings"]:
        for row in brief["earnings"]:
            lines.append(f"  - {row['date']}  {row['ticker']}")
    else:
        lines.append("  - Ninguno en la ventana consultada para el watchlist actual.")

    lines.append("\nTitulares recientes:")
    if brief["headlines"]:
        for h in brief["headlines"]:
            src = f" ({h['publisher']})" if h["publisher"] else ""
            lines.append(f"  - [{h['ticker']}] {h['title']}{src}")
    else:
        lines.append("  - Sin titulares disponibles.")

    lines.append("\nCalendario macro de referencia (frecuencia típica, confirma fechas exactas en la fuente oficial):")
    for m in brief["macro_reference"]:
        lines.append(f"  - {m['evento']}: {m['cuando']} · fuente: {m['fuente']} · impacto: {m['impacto']}")

    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Brief diario de noticias, resultados y eventos que pueden mover al mercado.")
    parser.add_argument("--indices", nargs="+", default=DEFAULT_INDICES, help="Tickers de índices/ETFs a monitorear")
    parser.add_argument("--watchlist", nargs="+", default=DEFAULT_WATCHLIST, help="Tickers a revisar por calendario de resultados")
    parser.add_argument("--news-tickers", nargs="+", default=DEFAULT_NEWS_TICKERS, help="Tickers de los que traer titulares")
    parser.add_argument("--earnings-days", type=int, default=7, help="Ventana en días hacia adelante para el calendario de resultados")
    parser.add_argument("--top-news", type=int, default=10, help="Máximo de titulares a mostrar")
    parser.add_argument("--demo", action="store_true", help="Genera un brief de ejemplo con datos sintéticos, sin red")
    parser.add_argument("--json-out", help="Ruta donde guardar el brief en JSON (además de imprimirlo en texto)")
    args = parser.parse_args()

    try:
        brief = build_brief(args)
    except Exception as exc:
        print(f"Error obteniendo datos en vivo: {exc}", file=sys.stderr)
        print("Sugerencia: revisa tu conexión a internet o usa --demo para ver el flujo con datos de ejemplo.", file=sys.stderr)
        sys.exit(1)

    print(render_text(brief))

    if args.json_out:
        with open(args.json_out, "w", encoding="utf-8") as f:
            json.dump(brief, f, ensure_ascii=False, indent=2)
        print(f"\nBrief guardado en {args.json_out}")


if __name__ == "__main__":
    main()
