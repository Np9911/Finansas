#!/usr/bin/env python3
"""
Calculadora de estrategia para pagar una hipoteca (u otro préstamo a cuotas
fijas) en un plazo objetivo, con comparación de escenarios.

Uso:
    python mortgage_payoff.py --principal 100000 --rate 6.5 --original-years 30 --target-years 5
    python mortgage_payoff.py --principal 100000 --rate 6.5 --original-years 30 --extra 500
    python mortgage_payoff.py --principal 100000 --rate 6.5 --original-years 30 --schedule-out plan.csv

Ver MORTGAGE_STRATEGY.md para las reglas y el resto de estrategias (quincenal,
aportes extra, refinanciar, costo de oportunidad).
"""

import argparse
import sys

import pandas as pd


def monthly_payment(principal, annual_rate, years):
    r = annual_rate / 12
    n = years * 12
    if r == 0:
        return principal / n
    return principal * r * (1 + r) ** n / ((1 + r) ** n - 1)


def amortize(principal, annual_rate, monthly_payment_amount, extra=0.0, max_months=600):
    r = annual_rate / 12
    balance = principal
    rows = []
    month = 0
    total_interest = 0.0
    payment = monthly_payment_amount + extra
    while balance > 0.01 and month < max_months:
        interest = balance * r
        principal_paid = payment - interest
        if principal_paid <= 0:
            raise ValueError("El pago mensual no cubre ni el interés — nunca se pagaría el préstamo.")
        if principal_paid > balance:
            principal_paid = balance
            payment_actual = principal_paid + interest
        else:
            payment_actual = payment
        balance -= principal_paid
        total_interest += interest
        month += 1
        rows.append({
            "mes": month,
            "pago": round(payment_actual, 2),
            "interes": round(interest, 2),
            "capital": round(principal_paid, 2),
            "saldo": round(max(balance, 0), 2),
        })
    return pd.DataFrame(rows), total_interest, month


def required_payment_for_years(principal, annual_rate, target_years):
    return monthly_payment(principal, annual_rate, target_years)


def required_rate_free_extra_for_years(principal, annual_rate, standard_payment, target_years, max_extra=50000):
    lo, hi = 0.0, max_extra
    target_months = target_years * 12
    for _ in range(60):
        mid = (lo + hi) / 2
        try:
            _, _, months = amortize(principal, annual_rate, standard_payment, extra=mid)
        except ValueError:
            lo = mid
            continue
        if months > target_months:
            lo = mid
        else:
            hi = mid
    return hi


def main():
    parser = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("--principal", type=float, default=100000, help="Saldo del préstamo")
    parser.add_argument("--rate", type=float, default=6.5, help="Tasa de interés anual, en %% (ej. 6.5)")
    parser.add_argument("--original-years", type=float, default=30, help="Plazo original del préstamo")
    parser.add_argument("--target-years", type=float, default=None, help="Años en los que quieres terminar de pagar")
    parser.add_argument("--extra", type=float, default=None, help="Extra mensual fijo a probar en vez de --target-years")
    parser.add_argument("--schedule-out", default=None, help="Ruta CSV para exportar la tabla de amortización del escenario acelerado")
    args = parser.parse_args()

    rate = args.rate / 100
    standard_payment = monthly_payment(args.principal, rate, args.original_years)
    _, standard_interest, standard_months = amortize(args.principal, rate, standard_payment)

    print(f"Préstamo: ${args.principal:,.2f} al {args.rate}% anual, plazo original {args.original_years:.0f} años")
    print(f"Pago mensual estándar: ${standard_payment:,.2f}")
    print(f"Interés total a plazo completo: ${standard_interest:,.2f} ({standard_months} meses)\n")

    if args.extra is not None:
        schedule, interest, months = amortize(args.principal, rate, standard_payment, extra=args.extra)
        print(f"Escenario: pago estándar + ${args.extra:,.2f} extra/mes = ${standard_payment + args.extra:,.2f}/mes")
    else:
        target_years = args.target_years if args.target_years is not None else 5
        target_payment = required_payment_for_years(args.principal, rate, target_years)
        extra_needed = target_payment - standard_payment
        schedule, interest, months = amortize(args.principal, rate, target_payment)
        print(f"Meta: pagar en {target_years:.0f} años")
        print(f"Pago mensual requerido: ${target_payment:,.2f}  (extra de ${extra_needed:,.2f}/mes sobre el estándar)")

    print(f"Meses reales para pagar: {months} ({months/12:.1f} años)")
    print(f"Interés total pagado: ${interest:,.2f}")
    print(f"Interés ahorrado vs. plazo original: ${standard_interest - interest:,.2f}")

    if args.schedule_out:
        schedule.to_csv(args.schedule_out, index=False)
        print(f"\nTabla de amortización guardada en {args.schedule_out}")


if __name__ == "__main__":
    main()
