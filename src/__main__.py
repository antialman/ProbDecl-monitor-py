#Example of creating the probDeclareMonitor, loading a model, and getting recommendations based on a prefix

import os
import operator

from probDeclPredictor import ProbDeclarePredictor


if __name__ == "__main__":
    modelPath = os.path.join("input", "model_01_probDecl.txt")
    prefix = ["b", "x", "b", "a", "a", "b"]

    probDeclarePredictor = ProbDeclarePredictor()
    probDeclarePredictor.loadProbDeclModel(modelPath)
    result = probDeclarePredictor.processPrefix(prefix)

    print("Final ranking:")
    for event, score in sorted(result.items(), key=operator.itemgetter(1), reverse=True):
        print("    " + str(event) + ": " + str(score)) #Using str(event) because result contains the keyword False for stopping the execution and the keyword True for any unknown activity