from decimal import Decimal


def calculate_iva(amount: Decimal, rule) -> Decimal:
    return (amount * rule.rate).quantize(Decimal('0.01'))


def calculate_isr(income: Decimal, rule) -> Decimal:
    """Bracket-based calculation from formula_expression."""
    brackets = rule.formula_expression.get('brackets', [])
    for bracket in brackets:
        if bracket['min'] <= income <= (bracket.get('max') or float('inf')):
            excess = income - Decimal(str(bracket['min']))
            tax = Decimal(str(bracket.get('fixed_fee', 0))) + excess * Decimal(str(bracket['rate']))
            return tax.quantize(Decimal('0.01'))
    return Decimal('0.00')