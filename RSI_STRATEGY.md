# Estrategia de reversión a la media con RSI diario

Estrategia táctica que complementa el portafolio base (`README.md`, `index.html`):
en vez de asignación pasiva, usa el **RSI(14) diario** para detectar y clasificar
oportunidades de entrada/salida dentro de una lista de activos (acciones, ETFs).

Herramienta: `rsi_screener.py`. Ver la sección "Cómo ejecutarlo" al final.

## Por qué RSI diario

El RSI (Relative Strength Index) mide la velocidad y magnitud de los movimientos
de precio en una escala de 0 a 100. En timeframe diario captura sobreventa y
sobrecompra de corto/mediano plazo sin el ruido de timeframes intradía, y es
suficientemente lento para ejecutarse una vez al día (revisión antes de la
apertura o al cierre), sin requerir monitoreo constante.

## Reglas de la estrategia

### Universo
Una lista de activos líquidos definida por el usuario (índices, ETFs sectoriales,
acciones large-cap). Evitar activos con poco volumen: el spread y el slippage
distorsionan una estrategia de swings de días/semanas.

### Filtro de tendencia
Solo se consideran señales de **compra** cuando `precio > SMA200` (media móvil de
200 días). Comprar sobreventa en una tendencia bajista de fondo ("catching a
falling knife") es el error más común de las estrategias RSI ingenuas: el filtro
de tendencia descarta esas señales.

### Señal de entrada (COMPRA)
RSI(14) cruza **hacia arriba** el nivel 30 (día anterior < 30, día actual ≥ 30),
con el filtro de tendencia activo. Se exige el cruce de confirmación —no solo
"RSI < 30"— para reducir entradas prematuras mientras el precio sigue cayendo.

### Señal de salida (VENTA / toma de ganancia)
RSI(14) cruza **hacia abajo** el nivel 70 (día anterior > 70, día actual ≤ 70).

### Stop-loss
-8% desde el precio de entrada. Es una regla dura, independiente del RSI: protege
contra el escenario en que el "rebote" nunca llega y el activo sigue cayendo.

### Salida por tiempo
Si la posición sigue abierta 60 días hábiles sin tocar el stop ni la toma de
ganancia, se cierra al precio de mercado. Evita mantener capital indefinidamente
inmovilizado en una posición que dejó de comportarse como reversión a la media.

### Gestión de riesgo y tamaño de posición
- Arriesgar como máximo **1–2% del capital total** por operación (definido por
  la distancia al stop-loss, no por el tamaño nominal de la posición).
- Máximo de posiciones simultáneas: 5–8, para mantener diversificación entre
  sectores/activos y no concentrar el riesgo en una sola señal.
- No promediar a la baja (no añadir capital a una posición que va en contra).

### Ranking de "mejores opciones"
Cada día, `rsi_screener.py` clasifica el universo en:

1. **COMPRA** — cruce de RSI confirmado hoy + tendencia alcista. Es la señal
   accionable.
2. **VIGILAR** — RSI entre 30 y 35, acercándose a zona de sobreventa; candidato
   para la próxima sesión.
3. **ESPERAR** — sin señal.
4. **VENTA / TOMA DE GANANCIA** — aplica a posiciones abiertas.

Dentro de "COMPRA", el orden final pondera el **desempeño histórico** de esa
misma regla sobre ese activo (win rate y retorno promedio por operación en el
backtest), no solo el RSI del día: dos activos con el mismo cruce hoy no son
igual de atractivos si uno tiene 65% de aciertos históricos y el otro 30%.

## Backtest incluido

`rsi_screener.py` corre automáticamente un backtest histórico de esta misma
regla (entrada/salida/stop/tiempo máximo) sobre cada ticker y reporta:

- número de operaciones históricas
- % de aciertos (win rate)
- retorno promedio por operación
- profit factor (ganancias totales / pérdidas totales)
- retorno compuesto acumulado si se hubieran tomado todas las señales

Esto da contexto para decidir si vale la pena seguir la señal de hoy en ese
activo específico, en vez de aplicar la regla a ciegas.

## Limitaciones (léelas antes de operar con dinero real)

- **RSI de reversión a la media funciona mejor en mercados laterales/rangos** y
  pierde efectividad en tendencias fuertes y sostenidas (por eso el filtro de
  SMA200, que mitiga pero no elimina el problema).
- El backtest usa una sola regla fija sobre datos históricos limitados: un buen
  resultado pasado no garantiza resultados futuros, y con pocas operaciones
  (`n` bajo) el win rate no es estadísticamente confiable.
- No incluye costos de transacción, impuestos ni slippage — en la práctica
  reducen el retorno neto, sobre todo en estrategias con muchas operaciones.
- Es una estrategia **táctica/activa**, complementaria al portafolio pasivo
  del `README.md`, no un sustituto. No es asesoría financiera personalizada.

## Cómo ejecutarlo

```bash
pip install -r requirements.txt

# Con datos reales (requiere acceso a internet; no funciona en este sandbox)
python rsi_screener.py --tickers SPY QQQ AAPL MSFT GOOGL AMZN NVDA META --period 2y

# Con tus propios datos (CSV por ticker: date,open,high,low,close,volume)
python rsi_screener.py --tickers AAPL MSFT --csv-dir ./mis_datos

# Modo demo (datos sintéticos, sin red) — para ver el flujo completo funcionando
python rsi_screener.py --demo
```

El resultado es una tabla ordenada de "mejores opciones" del día, con RSI,
estado, tendencia, señal y estadísticas del backtest por ticker. Ejecútalo cada
mañana antes de la apertura del mercado para tu revisión diaria.
