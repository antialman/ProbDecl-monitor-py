import os
import re
import itertools

import numpy as np

from Declare4Py.ProcessModels.DeclareModel import DeclareModel
from Declare4Py.ProcessModels.DeclareModel import DeclareModelTemplate
from Declare4Py.ProcessModels.LTLModel import LTLTemplate
from Declare4Py.ProcessModels.LTLModel import LTLModel

from logaut import ltl2dfa

from scipy.optimize import linprog

import ltlUtils


#Input model path
modelPath = os.path.join("input", "model_01_probDecl.txt")

int_char_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i', 9: 'l'} #Taken from Declare4Py.Utils.utils.parse_activity(act: str)
activityToEncoding = {} #Activity encodings, used internally to avoid issues with special characters in activity names
constraintFormulas = [] #Ltl formula of each constraint in the same order as they appear in the input model (with encoded activities)
formulaToProbability = {} #For looking up probabilities based on constraint formula
scenarios = [] #One tuple per each constraint scenario, tuples consist of 1,0 values where 1 means positive constraint and 0 means negated constraint
inconsistentScenarios = [] #Logically inconsistent scenarios
consistentScenarios = [] #Logically consistent scenarios
scenarioToDfa = {} #For looking up DFA based on scenario name, contains only consistent scenarios



#Reading the decl model
with open(modelPath, "r+") as file:
    for line in file:
        #Assuming <constraint>;<probability>
        splitLine = line.split(";")
        probability = float(splitLine[1].strip())
        constraintStr = splitLine[0].strip()
        
        if DeclareModel.is_constraint_template_definition(constraintStr):
            #Based on the method Declare4Py.ProcessModels.DeclareModel.parse(self, lines: [str])
            split = constraintStr.split("[", 1)
            template_search = re.search(r'(^.+?)(\d*$)', split[0])
            if template_search is not None:
                template_str, cardinality = template_search.groups()
                template = DeclareModelTemplate.get_template_from_string(template_str)
                if template is not None:
                    activities = split[1].split("]")[0]
                    activities = activities.split(", ")
                    tmp = {"template": template, "activities": activities,
                            "condition": re.split(r'\s+\|', constraintStr)[1:]}
                    if template.supports_cardinality:
                        tmp['n'] = 1 if not cardinality else int(cardinality)
                        cardinality = tmp['n']
                    
                    #Create activity encoding, if not already created
                    for activity in activities:
                        if activity not in activityToEncoding:
                            activityEncoding = str(len(activityToEncoding))
                            for int_key in int_char_map.keys():
                                activityEncoding = activityEncoding.replace(str(int_key), int_char_map[int_key])
                            activityToEncoding[activity] = activityEncoding
                    
                    #Create LTL formula for the constraint
                    formula = ltlUtils.get_constraint_formula(template,
                                                              activityToEncoding[activities[0]],
                                                              activityToEncoding[activities[1]] if template.is_binary else None,
                                                              cardinality)
                    formulaToProbability[formula] = probability
                    constraintFormulas.append(formula)
                    
                    print(formula)

print("Activity encodings: " + str(activityToEncoding))
print("======")
print("Reading decl file done")
print("======")


#Formula for enforcing simple trace semantics (requiring one proposition to hold at every time point, proposition z is intended for activities that are not present in the decl model)
#activityToEncoding[""] = "z" #Used for activities that are not in the decl model
#simpleTraceFormula = "(G((" + " || ".join(activityToEncoding.values()) + ") && " #At least one proposition must always be true
#acPairs = list(itertools.combinations(activityToEncoding.values(),2)) #Creates all possible activity pairs
#simpleTraceFormula = simpleTraceFormula + "(!(" + ")) && (!( ".join([" && ".join([ac for ac in acPair]) for acPair in acPairs]) + "))))" #At most one proposition must always be true
#print("Simple trace semantics formula (silently added to all scenarios): " + simpleTraceFormula)

#Formula for enforcing simple trace semantics (allowing all propositions to be false, should allow processing activities that are not present in the decl model by simply setting all propositions to false)
acPairs = list(itertools.combinations(activityToEncoding.values(),2))
simpleTraceFormula = "G((!(" + ")) && (!( ".join([" && ".join([ac for ac in acPair]) for acPair in acPairs]) + ")))" #At most one proposition can be true at any point in time
print("Simple trace semantics formula (silently added to all scenarios): " + simpleTraceFormula)


#Used for creating the constraint scenarios, 1 - positive constraint, 0 - negated constraint
scenarios = list(itertools.product([1, 0], repeat=len(constraintFormulas))) #Scenario with all positive constraints is first, and scenario with all negated constraints is last

#Creating automata for (and checking logical consistency of) each scenario
for  scenario in scenarios:
    formulaComponents = []
    for index, posneg in enumerate(scenario):
        if posneg == 1:
            #Add 1 to the scenario name and use the constraint formula as-is
            formulaComponents.append(constraintFormulas[index])
        else:
            #Add 0 to the scenario name and negate the constraint formula
            formulaComponents.append("(!" + constraintFormulas[index] + ")")
    
    scenarioFormula = " && ".join(formulaComponents) + " && " + simpleTraceFormula #Scenario formula is a conjunction of negated and non-negated constraint formulas + the formula to enforce simple trace semantics
    
    print("===")
    print("Scenario: " + "".join(map(str, scenario)))
    print("Formula: " + scenarioFormula)

    #Parsing the scenario formula
    scenarioModel = LTLModel()
    scenarioModel.to_ltlf2dfa_backend()
    scenarioModel.parse_from_string(scenarioFormula)
    print("Parsed formula: " + str(scenarioModel.parsed_formula))

    #Creating an automaton for the scenario and checking satisfiability
    scenarioDfa = ltl2dfa(scenarioModel.parsed_formula, backend="ltlf2dfa")
    if len(scenarioDfa.accepting_states) == 0:
        print("Satisfiable: False")
        inconsistentScenarios.append(scenario) #Name is used in the system of inequalities
    else:
        print("Satisfiable: True")
        consistentScenarios.append(scenario) #Name is used in the system of inequalities
        scenarioDfa = scenarioDfa.minimize() #Calling minimize seems to be redundant with the ltlf2dfa backend, but keeping the call just in case
        scenarioToDfa[scenario] = scenarioDfa #Used for processing the prefix and predicted events
        #print(str(scenarioDfa.to_graphviz()))

print("======")
print("Logical satisfiability checking done")
print("======")



#Creating the system of (in)equalities to calculate scenario probabilities
lhs_eq_coeficents = [[1] * len(scenarios)] #Sum of all scenarios...
rhs_eq_values = [1.0] #...equals 1

for formulaIndex, formula in enumerate(constraintFormulas):
    lhs_eq_coeficents.append([scenario[formulaIndex] for scenario in scenarios]) #Sum of scenarios where a constraint is not negated...
    rhs_eq_values.append(formulaToProbability[formula]) #...equals the probability of that constraint
#for i in range(len(rhs_eq_values)):
#    print(str(lhs_eq_coeficents[i]) + " = " + str(rhs_eq_values[i]))

bounds = [] #Tuples of upper and lower bounds for the value of each variable in the system of (in)equalities, where variables represent the probabilities of scenarios
for scenario in scenarios:
    if scenario in inconsistentScenarios:
        bounds.append((0,0)) #Probability of an inconsistent scenario must be 0
    else:
        bounds.append((0,1)) #Probability of a consistent scenario must be between 0 and 1

c = [[1] * len(scenarios)] #Leads to consistent probability values for all scenarios without optimizing for any scenario
#c[0][2]=2 #This would instead bias the solution towards assigning a higher probability to the third scenario (while adjusting the probabilities of other scenarios accordingly)
#print(c)

#Solving the system of (in)equalities
res = linprog(c, A_eq=lhs_eq_coeficents, b_eq=rhs_eq_values, bounds=bounds)
print(res.message)
if res.success:
    for scenarioIndex, scenarioProbability in enumerate(res.x):
        print("Scenario " + "".join(map(str, scenarios[scenarioIndex])) + " probability: " + str(scenarioProbability))
else:
    print("No event log can match input constraint probabilities") #For example, the probabilities of Existence[a] and Absence[a] must add up to 1 in every conceivable event log 



#Finding next possible events (and their probabilities) for a given trace prefix
prefix = [""]



#Example of replaying a prefix 
print()
for formulaCombination, scenarioDfa in scenarioToDfa.items():
    accepts = scenarioDfa.accepts([ 
        {}, #The automaton from ltl2dfa seems to always have an initial state with a single outgoing arc labeled true
        {activityToEncoding["b"]:True}, #Ocurrence of an event is represented by setting the corresponding proposition to true, other propositions remain false by default
        {}, #Activities that are not present in the decl model are represented as an empty dictionary (removing the empty dictionary would affect the processing of chain type constraints)
        {activityToEncoding["b"]:True}, 
        {activityToEncoding["a"]:True}, 
        {activityToEncoding["a"]:True}])

    if accepts:
        print("".join(map(str, formulaCombination)) + " accepts: " + str(accepts))
        #print(str(scenarioDfa.to_graphviz()))