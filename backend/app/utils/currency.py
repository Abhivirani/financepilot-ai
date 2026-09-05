def format_currency(amount: float | int | str) -> str:
    """
    Format a monetary value into Indian Rupee string representation with ₹ symbol
    and Indian digit grouping (e.g. ₹1,23,456.78).
    """
    try:
        num = float(amount)
    except (ValueError, TypeError):
        return "₹0.00"

    sign = "-" if num < 0 else ""
    abs_amt = abs(num)
    s = f"{abs_amt:.2f}"
    parts = s.split(".")
    integer_part = parts[0]
    decimal_part = parts[1]

    if len(integer_part) > 3:
        last_three = integer_part[-3:]
        other_digits = integer_part[:-3]
        res = ""
        while len(other_digits) > 2:
            res = "," + other_digits[-2:] + res
            other_digits = other_digits[:-2]
        res = other_digits + res + "," + last_three
    else:
        res = integer_part

    return f"{sign}₹{res}.{decimal_part}"
