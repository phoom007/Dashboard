def fmt_baht(v, no_prefix=False):
    try:
        v = float(v)
    except:
        return "-"
    s = f"{v:,.0f}"
    return s if no_prefix else f"฿{s}"

def fmt_pct(x, digits=2):
    if x is None:
        return "—"
    try:
        return f"{x*100:.{digits}f}%"
    except:
        return "—"
