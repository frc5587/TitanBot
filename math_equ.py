from sympy.solvers import solve
from sympy import Symbol, N
import mpmath as mp
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations, implicit_multiplication)
from typing import Union, List


def organize(input_string: List[str]) -> (Union[Symbol, None], str):
    """
    Takes the input from the user and discard the "-math" part and then finds the variable that they want to solve for
    and sets the equation equal to 0, if they aren't solving for a variable then it just passes it to the next step, it
    also removes all apaces
    :param input_string: the string that comes straight from the user
    :type input_string: str
    :return: variable/None is variable doesn't exist, string of equation
    :rtype: Union[Symbol, None], str
    """
    equation_str = ""
    variable, ignore = None, None
    for element in input_string:
        if element.lower() == '-v':
            index = input_string.index(element) + 1
            variable = Symbol(input_string[index])
            ignore = input_string[index]
        elif element != ignore:
            equation_str += element
    equation_str_copy = equation_str
    if '=' in equation_str:
        equation_str = f"({equation_str})".replace('=', ')-(')
    equation_str = equation_str.replace("^", "**").replace("e", str(mp.e))
    return variable, equation_str, equation_str_copy


def solve_equ(variable: Symbol, equation: str) -> List[str]:
    """
    If it is just an expression it will simplify it, otherwise it will solve it and return all possible answers in a
    list, with backticks (`) around it so it can be a little code segment with the discord markdown

    :param variable: sympy.Symbol
    :param equation: str
    :return: first element is all possible solutions
    :rtype: List[str]
    """
    answer = []
    if variable is None:
        return [f"`{N(equation)}`"]
    else:
        solved_answer = solve(equation, variable, dict=True)
    for ans in solved_answer:
        answer.append(f"`{variable} = {N(list(ans.values())[0])}`\n")
    return answer


def math_main(user_input: List[str]) -> (List[str], str):
    """
    Manages the solving process, first it organizes it, then it parse the str into an equation/expression, finally it
    solves/simplifies it then returns a list of answers

    :param user_input: content of the message
    :type user_input: str
    :return: list of answers, original equation
    :rtype: List[str], str
    """
    variable, equation, copy = organize(user_input)
    simplified_equ = parse_expr(equation, transformations=standard_transformations + (implicit_multiplication,))
    answers = solve_equ(variable, simplified_equ)
    return answers, copy
