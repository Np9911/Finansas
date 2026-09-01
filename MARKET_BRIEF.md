# Brief diario de mercado

Herramienta complementaria a las tres del `README.md`: no proyecta ni
recomienda, solo reúne en una lectura de dos minutos la información pública
que suele mover al mercado antes de la apertura — variación de índices y
volatilidad, calendario de resultados (earnings) de la semana, titulares
recientes y qué evento macroeconómico recurrente cae hoy.

Herramienta: `market_brief.py`. Ver la sección "Cómo ejecutarlo" al final.

## Qué reúne cada mañana

### Índices y volatilidad
Variación % del último cierre vs. el cierre previo para un watchlist de
índices/ETFs (por defecto `SPY QQQ DIA IWM`) y del VIX como proxy de
volatilidad implícita esperada para la sesión.

### Calendario de resultados (earnings)
Para un watchlist de tickers (por defecto ocho large-caps), busca fechas de
reporte de resultados dentro de una ventana de días hacia adelante
(7 por defecto). Un ticker con earnings próximos en una posición abierta es
información de riesgo, no solo de calendario.

### Titulares recientes
Últimos titulares disponibles por ticker, deduplicados, para los tickers de
`--news-tickers` (índices amplios + algunos nombres de alto peso por
defecto). Es un punto de partida para investigar, no un análisis de
sentimiento ni una señal de compra/venta.

### Eventos macro de hoy
Solo lo que se puede derivar de forma determinista de la fecha del día, sin
depender de un calendario económico en vivo:

- Todos los **jueves**: solicitudes iniciales de desempleo.
- **Primer viernes del mes** (regla típica, no garantizada todos los meses):
  reporte de empleo (Nonfarm Payrolls).

### Calendario macro de referencia
Una tabla estática de frecuencia/horario típico (no fechas exactas
descargadas) para los eventos de mayor impacto: CPI, PCE, decisión de tasas
del FOMC, ventas minoristas, ISM PMI. Sirve para saber qué vigilar cada mes,
no como fuente de la fecha puntual — esa se confirma en la fuente oficial
(`federalreserve.gov`, `bls.gov`, `bea.gov`, `ismworld.org`).

## Por qué no hay un calendario económico en vivo

Las fechas exactas de CPI, PCE, ventas minoristas y reuniones del FOMC no
siguen una regla fija de día del mes o del año — se publican con antelación
por cada agencia, pero requieren una fuente de calendario económico en vivo
(con su propia clave de API) para descargarse con precisión. Publicar una
fecha incorrecta como si fuera dato en vivo es peor que no publicarla: por
eso esta herramienta se limita a la frecuencia típica (referencia) y a los
dos únicos patrones que sí son deterministas por día de la semana (jueves y
primer viernes del mes).

## Limitaciones (léelas antes de operar con esta información)

- No pondera relevancia ni "importancia" de un titular más allá del orden
  en que la fuente de datos lo entrega — no es un resumen editorial ni un
  análisis de sentimiento.
- El calendario de resultados depende de que el proveedor de datos ya tenga
  confirmada la fecha; earnings anunciados con poca antelación pueden no
  aparecer a tiempo.
- La sección de eventos macro de hoy solo cubre dos patrones deterministas
  (jueves y primer viernes de mes); cualquier otro evento macro debe
  verificarse en la tabla de referencia y confirmarse en la fuente oficial.
- Es un agregador de información pública, no asesoría financiera
  personalizada. Complementa el análisis propio, no lo sustituye.

## Cómo ejecutarlo

```bash
pip install -r requirements.txt

# Con datos reales (requiere acceso a internet; no funciona en este sandbox)
python market_brief.py

# Con tu propio watchlist
python market_brief.py --indices SPY QQQ DIA IWM --watchlist AAPL MSFT GOOGL AMZN NVDA META TSLA JPM

# Guarda también el resultado en JSON
python market_brief.py --json-out brief.json

# Modo demo (datos sintéticos, sin red) — para ver el flujo completo funcionando
python market_brief.py --demo
```

El resultado es un resumen de texto en la terminal (y opcionalmente un JSON)
con índices, eventos macro de hoy, calendario de resultados y titulares.
Ejecútalo cada mañana antes de la apertura del mercado para tu revisión
diaria.
