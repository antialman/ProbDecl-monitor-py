from functools import reduce

from pythomata.core import DFA
from typing import TypeVar, Sequence

StateType = TypeVar("StateType")
SymbolType = TypeVar("SymbolType")


@staticmethod
def prefix_to_word(prefix: list[str], activityToEncoding: dict[str,str]) -> Sequence[SymbolType]:
    word = [{}]  #The automaton from ltl2dfa seems to always have an initial state with a single outgoing arc labeled true
    for activity in prefix:
        if activity in activityToEncoding:
            word.append({activityToEncoding[activity]:True}) #Ocurrence of an activity is represented by setting the corresponding proposition to true, other propositions remain false by default
        else:
            word.append({}) #Activities that are not present in the decl model are represented as an empty dictionary (removing the empty dictionary would affect the processing of chain type constraints)
    return word



#Returns the state of the automaton after processing a given word
#Based on FiniteAutomaton.accepts method from pythomata/core.py
@staticmethod
def get_state_for_prefix(aut: DFA, word: Sequence[SymbolType]) -> StateType:
    current_states = {aut.initial_state} #Reset the automaton to the initial state
    for symbol in word: #Find the automaton state after replaying the input word
            current_states = reduce(
                set.union,  # type: ignore
                map(lambda x: aut.get_successors(x, symbol), current_states),
                set(),
            )

    return list(current_states)[0] #The input is a DFA, so there must always be exactly one current state