# Ruta al Millón

Portafolio y simulador dirigidos a la meta de generar **$1,000,000 USD**, partiendo de:

- Capital inicial: **$10,000**
- Aporte mensual: **$500**
- Horizonte solicitado: **5 años**

## Herramienta interactiva

`index.html` es un simulador autónomo (sin dependencias de build): ajusta capital
inicial, aporte mensual y horizonte, y compara tres perfiles de riesgo
(conservador 6%, moderado 9%, agresivo 13% anual) en una gráfica de proyección con
capitalización mensual. Ábrelo directamente en el navegador.

## Estrategia táctica: screener RSI diario

`rsi_screener.py` complementa el portafolio pasivo con una estrategia activa de
reversión a la media basada en RSI(14) diario: cada día clasifica un universo de
activos por señal (compra/vigilar/esperar/venta) y los ranquea según el
desempeño histórico backtesteado de esa misma regla. Reglas completas,
gestión de riesgo y limitaciones en [`RSI_STRATEGY.md`](RSI_STRATEGY.md).

## Diagnóstico: ¿es realista $1,000,000 en 5 años?

No, con este capital y aporte. En 5 años se habrán aportado $10,000 + $500 × 60 =
**$40,000**. Convertir eso en $1,000,000 requiere un rendimiento anual sostenido de
**~83.7%** durante los 5 años completos — muy por encima de lo que ofrece cualquier
portafolio diversificado (acciones, bonos, ETFs). Rendimientos de esa magnitud solo
existen en apuestas concentradas de altísimo riesgo (opciones apalancadas, activos
altamente especulativos), donde el escenario más probable es la pérdida del capital,
no su multiplicación.

## Resultado realista a 5 años

| Perfil | Rendimiento anual | Valor final | Ganancia |
|---|---|---|---|
| Conservador | 6% | $48,548 | $8,548 |
| Moderado | 9% | $53,652 | $13,652 |
| Agresivo | 13% | $61,490 | $21,490 |

## Caminos realistas hacia $1,000,000

Manteniendo el mismo capital inicial ($10,000) y aporte mensual ($500):

| Camino | Rendimiento | Tiempo | Resultado |
|---|---|---|---|
| Mismo aporte, más paciencia | 9% anual | 30 años | $1,069,543 |
| Mismo aporte, más riesgo | 13% anual | 23 años | $1,061,976 |
| Mismo aporte, muy conservador | 6% anual | 39 años | $1,039,958 |
| Mismo horizonte (5 años), más aporte | 9% anual | 5 años | aporte mensual de **$12,596** |

Los otros dos apalancadores disponibles, sin cambiar el horizonte a 5 años, son
aumentar el aporte mensual muy por encima de lo actual, o asumir un riesgo
extremo con alta probabilidad de pérdida total. Ninguno de los dos sustituye una
estrategia diversificada.

## Portafolio recomendado por perfil

**Conservador** (~6% anual esperado)
- 45% Bonos (gobierno/corporativos)
- 35% ETF de acciones globales (mercado total)
- 15% Efectivo / fondo del mercado monetario
- 5% Oro / cobertura

**Moderado** (~9% anual esperado)
- 55% ETF de acciones globales (mercado total)
- 25% Bonos
- 12% Small-cap / growth
- 8% REITs (bienes raíces)

**Agresivo** (~13% anual esperado, alta volatilidad)
- 55% ETF de acciones globales (mercado total)
- 25% Small-cap / growth
- 12% Mercados emergentes
- 8% Activos especulativos (cripto, etc.)

## Plan de ejecución

1. **Automatiza el aporte mensual** — transferencia automática el día que llega tu ingreso.
2. **Diversifica con ETFs de bajo costo** — fondos indexados de amplio mercado (<0.2% anual) como base, no acciones individuales ni productos especulativos.
3. **Rebalancea una vez al año** — vuelve a la asignación objetivo de tu perfil.
4. **Sube el aporte cuando suba tu ingreso** — destina al menos la mitad de cada aumento salarial al portafolio; es la palanca más rápida para acortar el camino.

## Aviso

Este análisis usa capitalización mensual sobre tasas de retorno anual constantes;
los mercados reales varían año a año y el rendimiento pasado no garantiza
resultados futuros. No es asesoría financiera personalizada — antes de invertir,
considera consultar con un asesor financiero certificado sobre tu situación
específica.
