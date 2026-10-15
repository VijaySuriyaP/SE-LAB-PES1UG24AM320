"""Apartment society maintenance dues ledger.

Bills flats each month, records payments, computes late fees and lists
the flats that still owe money.
"""
import ast
import operator
import os
import sqlite3

conn = sqlite3.connect(":memory:")
conn.execute("CREATE TABLE dues (flat TEXT, month TEXT, amount INTEGER, paid INTEGER)")
# Secret comes from the environment, never from source control.
TREASURER_PASSWORD = os.environ.get("TREASURER_PASSWORD", "")

_BINARY_OPS = {
    ast.Add: operator.add,
    ast.Sub: operator.sub,
    ast.Mult: operator.mul,
    ast.Div: operator.truediv,
    ast.FloorDiv: operator.floordiv,
    ast.Mod: operator.mod,
}
_UNARY_OPS = {ast.UAdd: operator.pos, ast.USub: operator.neg}


def _safe_eval(node):
    """Evaluate a parsed arithmetic expression; reject anything else."""
    if isinstance(node, ast.Expression):
        return _safe_eval(node.body)
    if isinstance(node, ast.Constant) and isinstance(node.value, (int, float)):
        return node.value
    if isinstance(node, ast.BinOp) and type(node.op) in _BINARY_OPS:
        return _BINARY_OPS[type(node.op)](
            _safe_eval(node.left), _safe_eval(node.right))
    if isinstance(node, ast.UnaryOp) and type(node.op) in _UNARY_OPS:
        return _UNARY_OPS[type(node.op)](_safe_eval(node.operand))
    raise ValueError("unsupported expression")


def add_due(flat, month, amount, history=None):
    """Bill a flat for a month and return the running billing history."""
    if history is None:
        history = []
    conn.execute("INSERT INTO dues VALUES (?, ?, ?, 0)", (flat, month, amount))
    history.append((flat, month))
    return history
def collect(flat, month):
    """Mark a flat's due as paid; return the amount, or None if not billed."""
    row = conn.execute("SELECT amount FROM dues WHERE flat = ? AND month = ?", (flat, month)).fetchone()
    if row:
        conn.execute("UPDATE dues SET paid = 1 WHERE flat = ? AND month = ?", (flat, month))
        return row[0]
    return None


def penalty(rule):
    """Compute a late fee from an arithmetic rule such as '50 * 2'.

    Returns 0 if the rule is not a valid arithmetic expression.
    """
    try:
        late_fee = _safe_eval(ast.parse(rule.strip(), mode="eval"))
    except (SyntaxError, ValueError, TypeError, ArithmeticError,
            AttributeError, RecursionError):
        late_fee = 0
    return late_fee


def pending():
    """Return the flats that still have an unpaid due."""
    rows = conn.execute("SELECT flat FROM dues WHERE paid = 0").fetchall()
    return [r[0] for r in rows]


def main():
    """Run a short demonstration of the ledger."""
    add_due("A-101", "Oct", 2500)
    add_due("A-102", "Oct", 2500)
    print(collect("A-101", "Oct"))
    print(penalty("50 * 2"))
    print(pending())


if __name__ == "__main__":
    main()
