
print()
print("================")
print("=== ltlf2dfa ===")
print("================")
print()

from ltlf2dfa.parser.ltlf import LTLfParser

parser = LTLfParser()
formula_str = "G(a -> X b)"
formula = parser(formula_str)       # returns an LTLfFormula

print(formula)                      # prints "G(a -> X (b))"

dfa = formula.to_dfa()
print(dfa)                          # prints the DFA in DOT format(.venv)


print()
print("=============")
print("=== scipy ===")
print("=============")
print()

from scipy.optimize import root
from math import cos

def eqn(x):
  return x + cos(x)

myroot = root(eqn, 0)




print()
print("==================")
print("=== declare4py ===")
print("==================")
print()

import os

from Declare4Py.ProcessModels.LTLModel import LTLModel
from ltlf2dfa.parser.ltlf import LTLfParser
from logaut import ltl2dfa

model = LTLModel()
model.to_ltlf2dfa_backend() #Required to use the ltl2dfa instead of lydia for automata operations
model.parse_from_string("G(ER Triage -> F(CRP))")



parser = LTLfParser()
formula_str = "G(a -> WX b)"
formula = parser(formula_str)       # returns an LTLfFormula

print(formula)


model.parse_from_string("CRP")

model.add_eventually()
print(model.formula)
model.add_negation()
print(model.formula)
model.add_implication("F(Release A)")
print(model.formula)
print("--------------------------------\n")

model.parse_from_string("Leucocytes")
print(model.formula)
model.add_until("!(CRP)")
print(model.formula)
model.add_always()
print(model.formula)
print("--------------------------------\n")

model.parse_from_string("IV Liquid")
print(model.formula)
model.add_disjunction("IV Antibiotics")
print(model.formula)
model.add_conjunction("X[!](Admission NC)")
print(model.formula)
print("--------------------------------\n")

model.parse_from_string("Return ER")
print(model.formula)
model.add_next()
print(model.formula)
model.add_equivalence("Bad condition")
print(model.formula)

print("-------")


model.parse_from_string("!(X[!](true))") # si usa parse_ltl da pylogics.parsers
print(model.formula)
print(model.parsed_formula)
model.check_satisfiability()
dfa1 = ltl2dfa(model.parsed_formula, backend="ltlf2dfa")
dfa1 = dfa1.minimize()
print(dfa1.__dict__)
print(dfa1.accepts([{'a': True}, {'a': True}]))
print("-------")

model.parse_from_string("CRP & X[!](F(ER Triage && X[!](F(Admission NC))))")
print(f"{model.formula} is satisfiable? {model.check_satisfiability()}")

model.parse_from_string("G(CRP) && F(!(CRP))")
print(f"{model.formula} is satisfiable? {model.check_satisfiability(minimize_automaton=False)}" )


