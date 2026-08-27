# Estrategia: pagar $100,000 de hipoteca en 5 años

A diferencia de la meta de $1,000,000 (ver `README.md`), esta sí es alcanzable
con matemática de préstamo estándar — no requiere rendimientos extraordinarios,
solo un pago mucho más alto que el mínimo, sostenido durante 5 años.

Herramienta: `mortgage_payoff.py`. Ejemplo con supuestos por defecto ($100,000
al 6.5% anual, plazo original de 30 años):

```bash
python mortgage_payoff.py --principal 100000 --rate 6.5 --original-years 30 --target-years 5
```

## El número de referencia

| | Pago mensual | Interés total | Plazo real |
|---|---|---|---|
| Plan estándar (30 años) | $632 | $127,544 | 30 años |
| Plan acelerado (5 años) | $1,957 | $17,397 | 5 años |

Pagar en 5 años en vez de 30 cuesta **$1,325 extra al mes**, pero ahorra
**$110,148 en intereses**. Ajusta `--rate` y `--original-years` a tu préstamo
real — el pago requerido cambia mucho con la tasa.

## Estrategias, de la más simple a la más agresiva

### 1. Pago fijo acelerado
Compromete el pago mensual completo calculado arriba desde el primer mes.
Es la ruta más predecible: un solo número, sin depender de bonos ni ingresos
variables.

### 2. Pagos quincenales (biweekly)
Pagar la mitad del pago estándar cada dos semanas equivale a 26 medios pagos
= 13 pagos mensuales al año en vez de 12. Por sí sola, esta táctica lleva un
préstamo a 30 años a **~24 años**, no a 5 — es una mejora real pero
insuficiente como única estrategia para esta meta. Sirve como base combinada
con aportes extra.

### 3. Aportes extra al capital
Bonos, aguinaldo, devoluciones de impuestos, o cualquier ingreso no
recurrente, aplicados directamente al capital. Al hacer el pago, hay que
especificar explícitamente **"aplicar a capital"** (extra principal) — si no,
el banco puede registrarlo como pago adelantado del siguiente mes, que no
reduce el interés total.

### 4. Redondear o añadir un extra fijo mensual
Sumar una cantidad fija (ej. $500/mes) sin comprometerse al monto completo
calculado. Con $100,000 al 6.5%, $500 extra/mes lleva el préstamo de 30 a
**~10 años** — significativo, pero no llega a 5. `mortgage_payoff.py --extra`
calcula el resultado exacto para cualquier monto extra.

### 5. Refinanciar a un plazo corto
Refinanciar formalmente a un préstamo a 5 años (en vez de pagar extra sobre
uno a 30) da la misma cuota mensual pero como obligación contractual, a veces
con mejor tasa que el préstamo original. Contras: costos de cierre, y pierdes
la flexibilidad de reducir el pago a la cuota mínima en un mes difícil — con
pagos extra "voluntarios" sobre un préstamo a 30 años, siempre puedes volver
al mínimo si hace falta.

## Antes de empezar: verifica esto

- **Penalización por pago anticipado.** Algunos préstamos la tienen. Revisa
  el contrato antes de comprometerte a pagos extra agresivos.
- **Fondo de emergencia primero.** No conviene destinar cada dólar extra al
  préstamo si no hay 3-6 meses de gastos guardados aparte — un pago extra ya
  hecho no se puede "retirar" fácilmente en una emergencia.
- **Especifica "extra a capital"** en cada pago adicional (ver estrategia 3).

## Costo de oportunidad: ¿pagar extra o invertir?

Esta es la pregunta real detrás de la estrategia, y la respuesta depende de la
tasa del préstamo:

- Pagar extra al préstamo es un **retorno garantizado igual a la tasa de
  interés** (6.5% en el ejemplo) — sin riesgo, sin volatilidad.
- Invertir ese mismo dinero (ej. en un portafolio diversificado, ver
  `README.md`) tiene un retorno esperado potencialmente mayor a largo plazo
  (~9-10% histórico en acciones), pero no garantizado, y con volatilidad.

Con una tasa de préstamo **alta** (7%+), pagar extra es difícil de superar de
forma segura. Con una tasa **baja** (3-4%, común en préstamos de hace varios
años), invertir el extra suele ganar en expectativa, aunque con más riesgo e
incertidumbre. A 6.5% es una zona intermedia: ambas opciones son
razonables, y la elección depende de cuánto valoras la certeza (eliminar la
deuda) frente al retorno esperado más alto (invertir). Una estrategia mixta
— parte extra al préstamo, parte invertido — no es indecisión, es
diversificación de esa incertidumbre.
