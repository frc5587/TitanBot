from sympy.solvers import solve
from sympy import Symbol, N
import mpmath as mp
from sympy.parsing.sympy_parser import (parse_expr, standard_transformations, implicit_multiplication)
from typing import Union, List


def organize(input_string: str) -> (Union[Symbol, None], str):
    """
    Takes the input from the user and discard the "-math" part and then finds the variable that they want to solve for
    and sets the equation equal to 0, if they aren't solving for a variable then it just passes it to the next step, it
    also removes all spaces

    :param input_string: the string that comes straight from the user
    :type input_string: str
    :return: variable/None is variable doesn't exist, string of equation
    :rtype: Union[Symbol, None], str
    """
    element_list = input_string.split()
    element_list.pop(0)
    print_equ = ""
    variable, ignore = None, None
    for element in element_list:
        if element.lower() == '-v':
            index = element_list.index(element) + 1
            variable = Symbol(element_list[index])
            ignore = element_list[index]
        elif element != ignore:
            print_equ += element
    if '=' in print_equ:
        equation_str = f"({print_equ})".replace('=', ')-(')
    else:
        equation_str = print_equ
    equation_str = equation_str.replace("^", "**").replace("e", str(mp.e))
    return variable, equation_str, print_equ


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
        return [f"`{eval(str(N(equation)))}`"]
    else:
        solved_answer = solve(equation, variable, dict=True)
    for ans in solved_answer:
        answer.append(f"`{variable} = {N(list(ans.values())[0])}`\n")
    return answer


def math_main(user_input: str) -> (List[str], str):
    """
    Manages the solving process, first it organizes it, then it parse the str into an equation/expression, finally it
    solves/simplifies it then returns a list of answers

    :param user_input: content of the message
    :type user_input: str
    :return: list of answers, original equation
    :rtype: List[str], str
    """
    variable, equation, print_equ = organize(user_input)
    simplified_equ = parse_expr(equation, transformations=standard_transformations + (implicit_multiplication,))
    answers = solve_equ(variable, simplified_equ)
    return answers, print_equ
