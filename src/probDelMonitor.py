import os
import re

from Declare4Py.ProcessModels.DeclareModel import DeclareModel
from Declare4Py.ProcessModels.DeclareModel import DeclareModelTemplate


#Input model path
modelPath = os.path.join("input", "model_01_probDecl.txt")


formulaToProbability = {} #For looking up probabilities based on constraint formula
activityToEncoding = {} #Activity encodings, used internally to avoid issues with special characters in activity names


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
                    
                    
                    
                    print()
                    print(activities)
                    print(tmp)
                    print(constraintStr, template, str(cardinality))
                    
                    #self.constraints.append(tmp)
                    #declare_parsed_model.add_template(constraintStr, template, str(cardinality))
print(activityToEncoding)