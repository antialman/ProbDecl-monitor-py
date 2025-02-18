
from ltlf2dfa.parser.ltlf import LTLfParser

from Declare4Py.ProcessModels.LTLModel import LTLModel

from logaut import ltl2dfa


from scipy.optimize import linprog
import numpy as np

parser = LTLfParser()


#! ( <> ( ( \"A\" /\\ X(<>(\"A\")) ) ) )

#formula_str = "!(F(ac1))"
#formula_str = "!(F(a && X(F(b))))"
#formula_str = "G(a -> X(b))"
#formula_str = "!(F(ac1 && X(F(ac1 && X(F(ac1))))))"
#formula_str = "(F(ac1))"
formula_str = "(F(ac1 && (ac1 -> (X(F(ac1))))) && !(F(ac1 && (ac1 -> X(F(ac1 && (ac1 -> X(F(ac1)))))))))"
formula = parser(formula_str)       # returns an LTLfFormula

print(formula)                      # prints the formula

dfa = formula.to_dfa()
print(dfa)                          # prints the DFA in DOT format(.venv)



tp = (False, True, False)
print(tp[1])




print("#########")

formula_str = "(F(ac1 && (ac1 -> (X[!](F(ac1))))) && !(F(ac1 && (ac1 -> X[!](F(ac1 && (ac1 -> X[!](F(ac1)))))))))"
formula_str = "((!(ac2) U(ac1)) || (G(!(ac2))) && (!(ac2) || (!(X(ac1)) && !(X(!(ac1))))))"

scenarioModel = LTLModel()
scenarioModel.to_ltlf2dfa_backend()
scenarioModel.parse_from_string(formula_str)
print("Parsed formula: " + str(scenarioModel.parsed_formula))

scenarioDfa = ltl2dfa(scenarioModel.parsed_formula, backend="ltlf2dfa")
scenarioDfa = scenarioDfa.minimize() #Calling minimize seems to be redundant with the ltlf2dfa backend, but keeping the call just in case
print(str(scenarioDfa.to_graphviz()))


print("#########")
print("Checking Declare4Py.ProcessModels.LTLModel.parse_from_string(self, content: str, new_line_ctrl: str = '\\n')")
print("#########")

import sys
sys.path.append('./src')

from Declare4Py.ProcessModels.DeclareModel import DeclareModelTemplate
import ltlUtils

for template in DeclareModelTemplate:
    constraintFormula = ltlUtils.get_constraint_formula(template,
                                    "a",
                                    "b" if template.is_binary else None,
                                    1)
    print("Template: " + str(template))
    print("Formula: " + constraintFormula)
    scenarioModel = LTLModel()
    scenarioModel.to_ltlf2dfa_backend()
    scenarioModel.parse_from_string(constraintFormula)
    print("Parsed formula: " + str(scenarioModel.parsed_formula))
    scenarioDfa = ltl2dfa(scenarioModel.parsed_formula, backend="ltlf2dfa")
    print(str(scenarioDfa.to_graphviz()))
    print()

    if template is DeclareModelTemplate.ABSENCE or template is DeclareModelTemplate.EXISTENCE or template is DeclareModelTemplate.EXACTLY:
        constraintFormula = ltlUtils.get_constraint_formula(template,
                                        "a",
                                        "b" if template.is_binary else None,
                                        2)
        print("Template: " + str(template))
        print("Formula: " + constraintFormula)
        scenarioModel = LTLModel()
        scenarioModel.to_ltlf2dfa_backend()
        scenarioModel.parse_from_string(constraintFormula)
        print("Parsed formula: " + str(scenarioModel.parsed_formula))
        scenarioDfa = ltl2dfa(scenarioModel.parsed_formula, backend="ltlf2dfa")
        print(str(scenarioDfa.to_graphviz()))
        print()
    
    if template is DeclareModelTemplate.ABSENCE or template is DeclareModelTemplate.EXISTENCE:
        constraintFormula = ltlUtils.get_constraint_formula(template,
                                        "a",
                                        "b" if template.is_binary else None,
                                        3)
        print("Template: " + str(template))
        print("Formula: " + constraintFormula)
        scenarioModel = LTLModel()
        scenarioModel.to_ltlf2dfa_backend()
        scenarioModel.parse_from_string(constraintFormula)
        print("Parsed formula: " + str(scenarioModel.parsed_formula))
        scenarioDfa = ltl2dfa(scenarioModel.parsed_formula, backend="ltlf2dfa")
        print(str(scenarioDfa.to_graphviz()))
        print()
    

    
#System of inequalities

# Setting the inequality constraints matrix
A = np.array([[-1, -1, -1], 
              [-1, 2, 0], 
              [0, 0, -1], 
              [-1, 0, 0], 
              [0, -1, 0], 
              [0, 0, -1]])

# Setting the inequality constraints vector
b = np.array([-1000, 0, -340, 0, 0, 0])

# Setting the coefficients of the linear objective function vector
c = np.array([10, 15, 25])

# Solving linear programming problem
res = linprog(c, A_ub=A, b_ub=b)

print('Optimal value:', round(res.fun, ndigits=2),
      '\nx values:', res.x,
      '\nNumber of iterations performed:', res.nit,
      '\nStatus:', res.message)


############

# Setting the equality constraints matrix
A_eq = np.array([[  1 ,  1 ,  1 ,  1 ,  1 ,  1 ,  1 ,  1  ], 
              [  0 ,  1 ,  0 ,  1 ,  0 ,  1 ,  0 ,  1  ], 
              [  0 ,  0 ,  1 ,  1 ,  0 ,  0 ,  1 ,  1  ], 
              [  0 ,  0 ,  0 ,  0 ,  1 ,  1 ,  1 ,  1  ]])


b_eq = np.array([1.0, 1.0, 0.75, 0.5])

bounds = np.array([(0,0),(0,1),(0,1),(0,1),(0,0),(0,1),(0,0),(0,1)])


c = np.array([1 ,  1 ,  1 ,  1 ,  1 ,  1 ,  1 ,  1])

res = linprog(c, A_eq=A_eq, b_eq=b_eq, bounds=bounds)

print('Optimal value:', round(res.fun, ndigits=2),
      '\nx values:', res.x,
      '\nNumber of iterations performed:', res.nit,
      '\nStatus:', res.message)


lst = [1] * 5
print(lst)
lst[0]=0
print(lst)