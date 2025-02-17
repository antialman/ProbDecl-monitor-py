
from ltlf2dfa.parser.ltlf import LTLfParser

from Declare4Py.ProcessModels.LTLModel import LTLModel

from logaut import ltl2dfa

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
    

    
