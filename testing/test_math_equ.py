import pytest
import sympy
import math_equ


def test_organize():
    assert math_equ.organize(["3x=3", "-v", "x"]) == (sympy.Symbol('x'), "(3x)-(3)", "3x=3")
    assert math_equ.organize(["3^3"]) == (None, "3**3", "3^3")


def test_solve_equ():
    assert math_equ.solve_equ(sympy.Symbol('x'), "(3x)-(3)") == "x = 1"
    assert math_equ.solve_equ(None, '3**3') == "27"
