# Finansas

Una pequeña aplicación web con tres herramientas financieras interactivas —
inversión pasiva, trading táctico y pago de deuda — más los scripts de línea
de comandos detrás de cada una.

## Aplicación

Todo es HTML/CSS/JS autónomo, sin build ni dependencias de frontend. Para
verlo, abre `index.html` directamente en el navegador (o sirve la carpeta con
`python -m http.server` si prefieres navegar por URL).

| Página | Herramienta |
|---|---|
| `index.html` | Inicio — enlaza las tres herramientas |
| `portafolio.html` | **Ruta al Millón** — simulador de portafolio, tres perfiles de riesgo |
| `rsi.html` | **Screener RSI Diario** — estrategia de reversión a la media con backtest |
| `hipoteca.html` | **Cero Deuda en 5** — calculadora de pago acelerado de préstamos |

Las cuatro páginas comparten diseño, tipografía y navegación.

## Ruta al Millón — ¿es realista $1,000,000 en 5 años?

Portafolio dirigido a la meta de generar $1,000,000, partiendo de $10,000 de
capital inicial y $500 de aporte mensual.

No, con este capital y aporte. En 5 años se habrán aportado $10,000 + $500 × 60 =
**$40,000**. Convertir eso en $1,000,000 requiere un rendimiento anual sostenido de
**~83.7%** durante los 5 años completos — muy por encima de lo que ofrece cualquier
portafolio diversificado (acciones, bonos, ETFs). Rendimientos de esa magnitud solo
existen en apuestas concentradas de altísimo riesgo (opciones apalancadas, activos
altamente especulativos), donde el escenario más probable es la pérdida del capital,
no su multiplicación.

**Resultado realista a 5 años**

| Perfil | Rendimiento anual | Valor final | Ganancia |
|---|---|---|---|
| Conservador | 6% | $48,548 | $8,548 |
| Moderado | 9% | $53,652 | $13,652 |
| Agresivo | 13% | $61,490 | $21,490 |

**Caminos realistas hacia $1,000,000** (mismo capital y aporte)

| Camino | Rendimiento | Tiempo | Resultado |
|---|---|---|---|
| Mismo aporte, más paciencia | 9% anual | 30 años | $1,069,543 |
| Mismo aporte, más riesgo | 13% anual | 23 años | $1,061,976 |
| Mismo aporte, muy conservador | 6% anual | 39 años | $1,039,958 |
| Mismo horizonte (5 años), más aporte | 9% anual | 5 años | aporte mensual de **$12,596** |

**Portafolio recomendado por perfil**

- **Conservador** (~6%): 45% bonos, 35% ETF acciones globales, 15% efectivo, 5% oro
- **Moderado** (~9%): 55% ETF acciones globales, 25% bonos, 12% small-cap/growth, 8% REITs
- **Agresivo** (~13%): 55% ETF acciones globales, 25% small-cap/growth, 12% emergentes, 8% especulativo

**Plan de ejecución**: automatiza el aporte mensual, diversifica con ETFs de
bajo costo, rebalancea una vez al año, sube el aporte cuando suba tu ingreso.

## Screener RSI Diario

`rsi_screener.py` (y su interfaz en `rsi.html`) implementa una estrategia
activa de reversión a la media basada en RSI(14) diario: cada día clasifica
un universo de activos por señal (compra/vigilar/esperar/venta) y los
ranquea según el desempeño histórico backtesteado de esa misma regla.

```bash
pip install -r requirements.txt
python rsi_screener.py --tickers SPY QQQ AAPL MSFT --period 2y   # datos reales
python rsi_screener.py --demo                                    # sin red
```

Reglas completas, gestión de riesgo y limitaciones en
[`RSI_STRATEGY.md`](RSI_STRATEGY.md).

## Cero Deuda en 5 — pagar una hipoteca de $100,000 en 5 años

`mortgage_payoff.py` (y su interfaz en `hipoteca.html`) calcula el pago
mensual requerido para liquidar un préstamo en un plazo objetivo, compara
escenarios (quincenal, extra fijo, refinanciar) y exporta la tabla de
amortización. A diferencia de la meta de $1,000,000, esta sí es alcanzable
con matemática de préstamo estándar:

| | Pago mensual | Interés total | Plazo |
|---|---|---|---|
| Plan estándar (30 años, 6.5%) | $632 | $127,544 | 30 años |
| Plan a 5 años | $1,957 | $17,397 | 5 años |

```bash
python mortgage_payoff.py --principal 100000 --rate 6.5 --original-years 30 --target-years 5
```

Diagnóstico completo, cinco estrategias y la pregunta de costo de oportunidad
(pagar extra vs. invertir) en [`MORTGAGE_STRATEGY.md`](MORTGAGE_STRATEGY.md).

## Aviso

Todas las herramientas de este repositorio usan modelos financieros
simplificados con fines educativos y de planeación — capitalización mensual
sobre tasas constantes, sin costos de transacción, impuestos ni slippage. Los
mercados y las tasas reales varían; el rendimiento pasado no garantiza
resultados futuros. Nada aquí es asesoría financiera personalizada — antes de
tomar decisiones de inversión, deuda o trading, considera consultar con un
profesional certificado.
