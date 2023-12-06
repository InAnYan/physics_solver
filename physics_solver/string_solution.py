from typing import List, Tuple

import sympy
from sympy.physics.units import convert_to

from physics_solver.formulas import Formula
from physics_solver.problem import Problem
from physics_solver.problems.compare_problem import CompareProblem, Ordering
from physics_solver.problems.convert_problem import ConvertProblem
from physics_solver.problems.find_unknowns import FindUnknownsProblem
from physics_solver.problems.relative_change_problem import RelativeChangeProblem
from physics_solver.types import separate_num_and_unit, Variable, Quantity, Number, GivenVariable
from physics_solver.util import lmap


class StringSolution:
    givens: List[str]
    unknowns: List[str]
    steps: List[str]
    answer: str

    def __init__(self, problem: Problem, solution: object):
        # TODO: May be there would be problems with quantity printing because one 1.
        if isinstance(problem, ConvertProblem):
            solution: Quantity
            self.init_convert_problem(problem, solution)
        elif isinstance(problem, CompareProblem):
            solution: Ordering
            self.init_compare_problem(problem, solution)
        elif isinstance(problem, RelativeChangeProblem):
            solution: Tuple[float, Formula]
            self.init_relative_change_problem(problem, solution)
        elif isinstance(problem, FindUnknownsProblem):
            solution: List[Formula]
            self.init_find_unknowns_problem(problem, solution)
        else:
            raise NotImplemented()

    def init_convert_problem(self, problem: ConvertProblem, solution: Quantity):
        self.givens = [problem.given.__str__()]
        self.unknowns = [f'\\({problem.given.variable}({problem.target_unit}) - ?\\)']
        # TODO: Think about ConvertProblem StringSolution.steps.
        self.steps = [f'\\({problem.given.variable} = {problem.given.value} = {solution}\\)']
        self.answer = f'\\({solution}\\)'

    def init_compare_problem(self, problem: CompareProblem, solution: Ordering):
        self.givens = [f'\\({problem.x.variable}_1 = {problem.x.value}\\)',
                       f'\\({problem.y.variable}_2 = {problem.y.value}\\)']
        self.unknowns = [f'\\({problem.x.variable}_1 ? {problem.y.variable}_2\\)']
        if separate_num_and_unit(problem.x.value)[1] == separate_num_and_unit(problem.y.value):
            self.steps = []
        else:
            self.steps = [
                f'\\({problem.y.variable}_2 = {problem.y.value} = {convert_to(problem.y.value, separate_num_and_unit(problem.x.value)[1])}\\)']
        if solution == Ordering.EQ:
            self.answer = 'the quantities are equal'
        elif solution == Ordering.GT:
            self.answer = 'the first quantity is greater'
        else:
            self.answer = 'the second quantity is greater'

    def init_relative_change_problem(self, problem: RelativeChangeProblem, solution: Tuple[float, Formula]):
        (num, formula) = solution

        self.givens = []
        for change in problem.changes:
            self.givens.append(f'\\({change.variable}_2 = {change.factor}*{change.variable}_1\\)')

        self.unknowns = [f'\\({problem.y}_2 - ?\\)']

        step1 = fraction(problem.y.__str__() + '_2', problem.y.__str__() + '_1')

        first_subs = formula.expansion.subs(lmap(lambda c: (c.variable, Variable(c.variable.__str__() + '_1')),
                                                 problem.changes))
        second_subs = formula.expansion.subs(lmap(lambda c: (c.variable, Variable(c.variable.__str__() + '_2')),
                                                  problem.changes))
        step2 = fraction(second_subs, first_subs)

        second_subs_change = formula.expansion.subs(
            lmap(lambda c: (c.variable, c.factor * Variable(c.variable.__str__() + '_1')),
                 problem.changes))
        step3 = fraction(second_subs_change, first_subs)

        self.steps = [f"\\({step1} = {step2} = {step3} = {num}\\)"]

        if num < 1:
            self.answer = f'the variable will decrease by a factor of {1 / num}'
        elif num == 1:
            self.answer = 'the variable will not change'
        else:
            self.answer = f'the variable will increase by a factor of {num}'

    def init_find_unknowns_problem(self, problem: FindUnknownsProblem, solution: List[Formula]):
        self.givens = lmap(lambda g: g.__str__(), problem.givens)

        self.unknowns = lmap(lambda u: f'\\({u} - ?\\)', problem.unknowns)

        self.steps = []
        state = problem.givens.copy()
        for formula in solution:
            value = sympy.simplify(formula.expansion.subs(lmap(lambda g: g.to_tuple(), state)))
            # TODO: Values are not quantities but mul.
            # assert isinstance(value, Quantity)
            state.append(GivenVariable(formula.var, value))
            self.steps.append(f'\\({formula.var} = {formula.expansion} = {value}\\)')

        self.answer = f'\\({state[-1].value}\\)'


def fraction(a: object, b: object) -> str:
    return '\\dfrac{' + a.__str__() + '}{' + b.__str__() + '}'
