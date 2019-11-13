from typing import List, Union

import mpmath as mp
import sympy
import sympy.parsing.sympy_parser as sympy_parser


def organize(equation_list: List[str]) -> (Union[sympy.Symbol, None], str):
    """
    Takes the input from the user and discard the "-math" part and then finds the variable that they want to solve for
    and sets the equation equal to 0, if they aren't solving for a variable then it just passes it to the next step, it
    also removes all spaces
    :param equation_list: the list containing elements that describe the equation to process
    :type equation_list: List[str]
    :return: variable/None is variable doesn't exist, string of equation
    :rtype: Union[sympy.Symbol, None], str
    """
    equation_str = ""
    variable, ignore = None, None
    for element in equation_list:
        if element.lower() == '-v':
            index = equation_list.index(element) + 1
            variable = sympy.Symbol(equation_list[index])
            ignore = equation_list[index]
        elif element != ignore:
            equation_str += element
    equation_str_copy = equation_str
    if '=' in equation_str:
        equation_str = f"({equation_str})".replace('=', ')-(')
    equation_str = equation_str.replace("^", "**").replace("e", str(mp.e))
    return variable, equation_str, equation_str_copy


def solve_equ(variable: sympy.Symbol, equation: str) -> List[str]:
    """
    If it is just an expression it will simplify it, otherwise it will solve it and return all possible answers in a
    list, with backticks (`) around it so it can be a little code segment with the discord markdown

    :param variable: sympy.sympy.Symbol
    :param equation: str
    :return: first element is all possible solutions
    :rtype: List[str]
    """
    answer = []
    if variable is None:
        return [f"`{sympy.N(equation)}`"]
    else:
        solved_answer = sympy.solve(equation, variable, dict=True)
    for ans in solved_answer:
        answer.append(f"`{variable} = {sympy.N(list(ans.values())[0])}`\n")
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
    simplified_equ = sympy_parser.parse_expr(
        equation,
        transformations=sympy_parser.standard_transformations +
        (sympy_parser.implicit_multiplication,))
    answers = solve_equ(variable, simplified_equ)
    return answers, copy
