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

activityToEncoding = {} #Activity encodings, used internally to avoid issues with special characters in activity names
ltlFormulas = [] #List of ltl formulas (with encoded activities)
formulaToProbability = {} #For looking up probabilities based on constraint formula



#Reading the decl model
with open(modelPath, "r+") as file:
    for line in file:
        #Assuming <constraint>;<probability>
        splitLine = line.split(";")
        probability = float(splitLine[1].strip())
        constraintStr = splitLine[0].strip()
        
        if DeclareModel.is_constraint_template_definition(constraintStr):
            #Based on the parse(self, lines: [str]) method in Declare4Py.ProcessModels.DeclareModel
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
                            activityToEncoding[activity] = "ac" + str(len(activityToEncoding))
                    
                    #Create LTL formula for the constraint
                    formula = ltlUtils.get_constraint_formula(template,
                                                              activityToEncoding[activities[0]],
                                                              activityToEncoding[activities[1]] if template.is_binary else None,
                                                              cardinality)
                    formulaToProbability[formula] = probability
                    ltlFormulas.append(formula)
                    
                    print(formula)
    
    print("======")
    print("Reading decl file done")
    print("======")

    #Creating formula for enforcing simple trace semantics
    activityToEncoding[""] = "acx" #Used for activities that are not in the decl model (needed for chain constraints)
    simpleTraceFormula = "(G(" + " || ".join(activityToEncoding.values()) + ") && " #At least one proposition must always be true
    acPairs = list(itertools.combinations(activityToEncoding.values(),2)) #Creates all possible activity pairs
    simpleTraceFormula = simpleTraceFormula + "(!(" + ")) && (!( ".join([" && ".join([ac for ac in acPair]) for acPair in acPairs]) + ")))" #At most one proposition must always be true
    print("Simple trace semantics formula (silently added to all scenarios): " + simpleTraceFormula)


    #Used for creating the constraint scenarios, false means the corresponding constraint will be negated in the specific scenario 
    formulaCombinations = list(itertools.product([True, False], repeat=len(ltlFormulas)))
    
    #Creating automata for (and checking logical consistency of) each scenario
    for  formulaCombination in formulaCombinations:
        nameComponents = ["x"]
        formulaComponents = []
        for index, formulaBoolean in enumerate(formulaCombination):
            if formulaBoolean:
                nameComponents.append("1")
                formulaComponents.append(ltlFormulas[index])
            else:
                nameComponents.append("0")
                formulaComponents.append("(!" + ltlFormulas[index] + ")")
        
        scenarioName = "".join(nameComponents)
        scenarioFormula = " && ".join(formulaComponents) + " && " + simpleTraceFormula
        
        print("===")
        print("Scenario: " + scenarioName)
        print("Formula: " + scenarioFormula)

        scenarioModel = LTLModel()
        scenarioModel.to_ltlf2dfa_backend()
        scenarioModel.parse_from_string(scenarioFormula)

        print("Satisfiability: " + str(scenarioModel.check_satisfiability()))






