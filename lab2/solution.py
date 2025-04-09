from functools import reduce
import re
from typing import List, NamedTuple, Set


class Literal(NamedTuple):
    name: str
    negated: bool
    clauseId: int
    parentIds: List[int]

    def __repr__(self):
        return  formatLiteral(self)
    
    def __invert__(self):
        return CreateLiteral(self.name, not self.negated)
    
    def __eq__(self, value: object) -> bool:
        if(type(value) is not Literal):
            return False
        return self.name == value.name and self.negated == value.negated
Clause = Set[Literal]
    
def CreateLiteral(name: str, negated: bool):
    return Literal(name, negated, 0, [0, 0])

def CreateLiteralWithParents(name: str, negated: bool, parent1:int, parent2:int):
    return Literal(name, negated, 0, [parent1, parent2])

def parseInputData(filename: str):
    f = open(filename)
    line = f.readline().lower().strip()

    clauses: List[Set[Literal]] = []

    # for each line
    while line != "":

        # if line is comment, continue
        if(line.startswith("#")):
            continue

        # create set from line
        literals = set()
        for literal in line.split(' v '):
            if(literal[0] == '~'):
                literals.add(CreateLiteral(literal[1:], True))
                continue
            literals.add(CreateLiteral(literal, False))

        clauses.append(literals)

        line = f.readline().lower().strip()

    return clauses
        

def resolvents(A: Set[Literal], B: Set[Literal]):
    res: List[Set[Literal]] = []
    for literal in A:
        if(~literal in B):
            C = A.difference([literal]).union(B.difference([~literal]))
            res.append(C)
    return res



def isTautology(clause: Set[Literal]) -> bool:
    # negSet = { ~literal for literal in clause } # ne radi jer me pylance je*e
    negSet: Set[Literal] = set([~lit for lit in clause])
    return len( clause.intersection(negSet) ) != 0

clauseCounter: int = 1
def printClause(clause: Clause):
    global clauseCounter
    # TODO: get count from object
    if(isNil(clause)):
        print("_|_ (nil)")
        return
    clauseList = list(clause)
    print(f"{clauseCounter}. {clauseList[0]}{reduce(lambda s, l : s + ' v ' + formatLiteral(l), clauseList[1:], '')}")
    clauseCounter += 1

def formatLiteral(literal: Literal):
    return f"{'~' if literal.negated else ''}{literal.name}"

def isNil(clause: Clause):
    return len( clause ) == 0


def main() :
    clauses: List[Clause] = parseInputData("input.txt")
    ## Set Of Support , Skup potpore
    sos = [clauses[-1]]
    clauses = clauses[:-1]

    for clause in clauses:
        printClause(clause)

    print("==============")

    res = resolvents(clauses[3], clauses[2])
    for i in range(len(res) -1, -1, -1):
        r = res[i]
        if(isNil(r)):
            print("FOUND NIL, exiting")
            exit(1)
        
        ## maknuti taut
        if(isTautology(r)):
            res.pop(i)

    ## TODO strategija brisanja, redundantne klauzule

    for r in res:
        printClause(r)



if __name__ == "__main__":
    main()

