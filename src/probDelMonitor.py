import os
import re
import itertools

import numpy as np

from Declare4Py.ProcessModels.DeclareModel import DeclareModel
from Declare4Py.ProcessModels.DeclareModel import DeclareModelTemplate
from Declare4Py.ProcessModels.LTLModel import LTLTemplate
from Declare4Py.ProcessModels.LTLModel import LTLModel

from logaut import ltl2dfa

import ltlUtils


#Input model path
modelPath = os.path.join("input", "model_01_probDecl.txt")

int_char_map = {0: 'a', 1: 'b', 2: 'c', 3: 'd', 4: 'e', 5: 'f', 6: 'g', 7: 'h', 8: 'i', 9: 'l'} #Taken from Declare4Py.Utils.utils.parse_activity(act: str)
activityToEncoding = {} #Activity encodings, used internally to avoid issues with special characters in activity names
constraintFormulas = [] #Ltl formula of each constraint in the same order as they appear in the input model (with encoded activities)
formulaToProbability = {} #For looking up probabilities based on constraint formula
inconsistentScenarios = []
consistentScenarios = []
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


#Formula for enforcing simple trace semantics (requiring one proposition to hold at every time point and proposition z used for activities that are not present in the decl model)
#activityToEncoding[""] = "z" #Used for activities that are not in the decl model
#simpleTraceFormula = "(G((" + " || ".join(activityToEncoding.values()) + ") && " #At least one proposition must always be true
#acPairs = list(itertools.combinations(activityToEncoding.values(),2)) #Creates all possible activity pairs
#simpleTraceFormula = simpleTraceFormula + "(!(" + ")) && (!( ".join([" && ".join([ac for ac in acPair]) for acPair in acPairs]) + "))))" #At most one proposition must always be true
#print("Simple trace semantics formula (silently added to all scenarios): " + simpleTraceFormula)

#Formula for enforcing simple trace semantics (allowing all propositions to be false)
acPairs = list(itertools.combinations(activityToEncoding.values(),2))
simpleTraceFormula = "G((!(" + ")) && (!( ".join([" && ".join([ac for ac in acPair]) for acPair in acPairs]) + ")))" #At most one proposition must always be true
print("Simple trace semantics formula (silently added to all scenarios): " + simpleTraceFormula)


#Used for creating the constraint scenarios, false means the corresponding constraint will be negated in the specific scenario 
formulaCombinations = list(itertools.product([True, False], repeat=len(constraintFormulas)))

#Creating automata for (and checking logical consistency of) each scenario
for  formulaCombination in formulaCombinations:
    nameComponents = ["x"]
    formulaComponents = []
    for index, formulaBoolean in enumerate(formulaCombination):
        if formulaBoolean:
            #Add 1 to the scenario name and use the constraint formula as-is
            nameComponents.append("1")
            formulaComponents.append(constraintFormulas[index])
        else:
            #Add 0 to the scenario name and negate the constraint formula
            nameComponents.append("0")
            formulaComponents.append("(!" + constraintFormulas[index] + ")")
    
    scenarioName = "".join(nameComponents) #Joins the scenario name into a single string, e.g., x001, which would mean negation of the first and second constraint
    scenarioFormula = " && ".join(formulaComponents) + " && " + simpleTraceFormula #Scenario formula is a conjunction of negated and non-negated constraint formulas + the formula to enforce simple trace semantics
    
    print("===")
    print("Scenario: " + scenarioName)
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
        inconsistentScenarios.append(scenarioName) #Name is used in the system of inequalities
    else:
        print("Satisfiable: True")
        consistentScenarios.append(scenarioName) #Name is used in the system of inequalities
        scenarioDfa = scenarioDfa.minimize() #Calling minimize seems to be redundant with the ltlf2dfa backend, but keeping the call just in case
        scenarioToDfa[scenarioName] = scenarioDfa #Used for processing the prefix and predicted events
        print(str(scenarioDfa.to_graphviz()))





print()
for scenarioName, scenarioDfa in scenarioToDfa.items():
    accepts = scenarioDfa.accepts([
        {activityToEncoding["a"]:True},
        {activityToEncoding["a"]:True}, 
        {activityToEncoding["b"]:True}, 
        {activityToEncoding["a"]:True}, 
        {activityToEncoding["b"]:True}])


    print(scenarioName + " accepts: " + str(accepts))

    
        






