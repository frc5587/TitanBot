import sys
import os.path

import sympy

sys.path.append(  # import from directory above
    os.path.abspath(os.path.join(os.path.dirname(__file__), os.path.pardir)))

import math_equ


def test_organize():
    assert math_equ.organize(["3x=3", "-v", "x"]) == (sympy.Symbol('x'), "(3x)-(3)", "3x=3")
    assert math_equ.organize(["3^3"]) == (None, "3**3", "3^3")


def test_parse_equ():
    assert math_equ.parse_equ("(3x)-(3)") == 3*sympy.Symbol('x') - 3
    assert math_equ.parse_equ('3**3') == 27


def test_solve_equ():
    assert math_equ.solve_equ(sympy.Symbol('x'), 3*sympy.Symbol('x') - 3)
    assert math_equ.solve_equ(None, 27)


def test_math_main():
    assert math_equ.math_main(["3x=3", "-v", "x"]) == (['x = 1.00000000000000\n'], '3x=3')
    assert math_equ.math_main(["3^3"]) == (['`27.0000000000000`'], '3^3')
