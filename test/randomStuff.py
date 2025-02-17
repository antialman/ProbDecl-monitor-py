
from ltlf2dfa.parser.ltlf import LTLfParser

parser = LTLfParser()


#! ( <> ( ( \"A\" /\\ X(<>(\"A\")) ) ) )

#formula_str = "!(F(ac1))"
#formula_str = "!(F(ac1 && X(F(ac1))))"
#formula_str = "!(F(ac1 && X(F(ac1 && X(F(ac1))))))"
formula_str = "(F(ac1))"
formula = parser(formula_str)       # returns an LTLfFormula

print(formula)                      # prints the formula

dfa = formula.to_dfa()
print(dfa)                          # prints the DFA in DOT format(.venv)



tp = (False, True, False)
print(tp[1])