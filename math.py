from sympy import N
from sympy.solvers import solve
from sympy import Symbol
import mpmath as mp
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations, implicit_multiplication)


def organize(start_string):
    """
    Takes the input from the user and discard the "-math" part and then find the variable that they want to solve for
    and sets the equation equal to 0, if they aren't solving for a variable then it just passes it to the next step

    :param: str
    :return: tuple
    """
    equ_list = start_string.split()
    equ_list.pop(0)
    equ_str = ""
    variable_bool = False
    varible = None
    for i in equ_list:
        if i is None:
            continue
        elif i.lower() == '-v':
            location = equ_list.index(i) + 1
            varible = Symbol(equ_list[location])
            equ_list[location] = None
            variable_bool = True
        else:
            equ_str += i
    if '=' in equ_str:
        equ_str = f"({equ_str})".replace('=', ')-(')
    equ_str = equ_str.replace("^", "**").replace("e", str(mp.e))
    return (variable_bool, varible, equ_str)


def solve_equ(variable, equ):
    """
    If it is just an expression it will simplify it, otherwise it will solve it and return all possible answers in a
    list

    :param variable: sympy.Symbol
    :param equ: str
    :return: list
    """
    ans = []
    if variable is None:
        return [f"`{N(equ)}`"]
    else:
        partial_ans = solve(equ, variable, dict=True)
    for i in partial_ans:
        ans.append(f"{variable} = `{N(list(i.values())[0])}`\n")
    return ans


def math_main(user_input):
    """
    Manages the solving process, first it organizes it, then it parse the str into an equation/expression, finally it
    solves/simplifies it then returns a list of answers

    :param user_input: str
    :return: list
    """
    set_pieces = organize(user_input)
    simplified_equ = parse_expr(set_pieces[2], transformations=standard_transformations + (implicit_multiplication,))
    answers = solve_equ(set_pieces[1], simplified_equ)
    return answers
