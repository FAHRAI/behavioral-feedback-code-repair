"""Counts for paired strict-acceptance outcomes."""


def contrast(rows):
    n = len(rows)
    b = sum(r["B"]["S"] for r in rows)
    c = sum(r["C"]["S"] for r in rows)
    return {
        "n": n,
        "B": b,
        "C": c,
        "C_minus_B_pp": 100 * (c - b) / n if n else None,
        "C_only": sum(r["C"]["S"] and not r["B"]["S"] for r in rows),
        "B_only": sum(r["B"]["S"] and not r["C"]["S"] for r in rows),
    }
