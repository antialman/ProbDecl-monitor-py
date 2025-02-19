#Example of creating the probDeclareMonitor, loading a model, and getting recommendations based on a prefix

import os
import operator

from probDeclPredictor import ProbDeclarePredictor


if __name__ == "__main__":
    #Loading the probDeclare model
    modelPath = os.path.join("input", "model_01_probDecl.txt")
    probDeclarePredictor = ProbDeclarePredictor()
    probDeclarePredictor.loadProbDeclModel(modelPath)

    #Processing trace prefix (no need to reload the model after each prefix)
    prefixes = [["b", "x", "b", "a", "a"],["b", "x", "b", "a", "a", "a"]]
    for prefix in prefixes:
        result = probDeclarePredictor.processPrefix(prefix)

        #Example of processing the output ranking
        print("Ranking for prefix " + str(prefix) + ":")
        for event, score in sorted(result.items(), key=operator.itemgetter(1), reverse=True):
            if event is True:
                #Excecution of any event that is not present in the declare model
                print("    Unknown: " + str(score))
            elif event is False:
                #Stopping the execution at the end of the given prefix
                print("    Stop: " + str(score))
            else:
                #Execution of an activity that present in the declare model
                print("    " + event + ": " + str(score))