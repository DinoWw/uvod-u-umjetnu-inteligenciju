import sys
from collections import defaultdict
from functools import reduce
from operator import index
import random
from typing import Dict, List, NamedTuple, Set


class Literal(NamedTuple):
    name: str
    negated: bool

    def __repr__(self):
        return  formatLiteral(self)
    
    def __invert__(self):
        return CreateLiteral(self.name, not self.negated)
    
    def __eq__(self, value: object) -> bool:
        if(type(value) is not Literal):
            return False
        return self.name == value.name and self.negated == value.negated
    # def __hash__(self) -> int:
    #     return hash(self.name) + self.negated

CNF = Set[Literal]

def CreateLiteral(name: str, negated: bool):
    return Literal(name, negated)

class Clause(NamedTuple):
    clause: CNF
    id: int
    parents: List[int]

clauseCounter: int = 0
indexedClauses: List[Clause] = []
freeCombs: Dict[int, Set[int]] = dict()
def createClause(clause: CNF, parents: List[int]):
    global clauseCounter
    newClause = Clause(clause, clauseCounter, parents)
    indexedClauses.append(newClause)
    clauseCounter += 1

    ## keep freeCombs up to date
    freeCombs[newClause.id] = {i for i in range(0, newClause.id)}

    return newClause

def parseInputData(filename: str):
    global clauseCounter
    f = open(filename)
    line = f.readline().lower().strip()

    clauses: List[Clause] = []

    # for each line
    while line != "":

        # if line is comment, continue
        if(line.startswith("#")):
            continue

        # create set from line
        literals: CNF = set()
        for literal in line.split(' v '):
            if(literal[0] == '~'):
                literals.add(CreateLiteral(literal[1:], True))
                continue
            literals.add(CreateLiteral(literal, False))

        clauses.append(createClause(literals, []))

        line = f.readline().lower().strip()

    return clauses
        

def resolvents(Ad: Clause, Bd: Clause):
    A = Ad.clause
    B = Bd.clause
    res: List[Clause] = []
    for literal in A:
        if(~literal in B):
            C = A.difference([literal]).union(B.difference([~literal]))
            res.append(createClause(C, [Ad.id, Bd.id]))
    return res

def isTautology(clause: Set[Literal]) -> bool:
    # negSet = { ~literal for literal in clause } # ne radi jer me pylance je*e
    negSet: Set[Literal] = set([~lit for lit in clause])
    return len( clause.intersection(negSet) ) != 0

def negateClause(clause: Clause) -> List[Clause]:
    # adding parents would cause recursion in other parts of code
    # also does not really make sense
    return [createClause(set([~literal]), []) for literal in clause.clause]

def printClause(clause: Clause):
    if(isNil(clause.clause)):
        print(f"{clause.id}. _|_ (nil) {clause.parents}")
        return
    clauseList = list(clause.clause)
    print(f"{clause.id}. {clauseList[0]}{reduce(lambda s, l : s + ' v ' + formatLiteral(l), clauseList[1:], '')} {clause.parents}")

def formatLiteral(literal: Literal):
    return f"{'~' if literal.negated else ''}{literal.name}"

def isNil(clause: CNF):
    return len( clause ) == 0


pickedPairs: Dict[int, Set[int]] = defaultdict(set[int])
def pickClauses(original: List[Clause], sos: List[Clause]):
    if( len( freeCombs.keys()) == 0 ):
        print("no match")
        exit(1)

    index1 = random.choice(list(freeCombs.keys()))
    index2 = freeCombs[index1].pop()

    if ( len( freeCombs[index1] ) == 0 ):
        del freeCombs[index1]

    if(index2 < len(original)):
        ca = original[index2]
    else:
        ca = sos[index2 - len(original)]

    return ca, sos[index1 - len(original)]
    




def main() :
    if (len(sys.argv) != 3):
        raise ValueError("supply alg and filename as arguments")
    alg = sys.argv[1]
    filename = sys.argv[2]
    
    clauses: List[Clause] = parseInputData(filename)

    for clause in clauses:
        printClause(clause)

    goalClause = clauses.pop()
    indexedClauses.pop()    # the original goal clause should never be referenced, only its negations from sos
    global clauseCounter
    clauseCounter -= 1
    ## Set Of Support , Skup potpore
    sos: List[Clause] = negateClause(goalClause)

    ## clauses fom base set should not be in freeCombs
    for c in clauses:
        del freeCombs[c.id]


    print("==============")

    goalFound = False
    while(not goalFound):
        c1, c2 = pickClauses(clauses, sos)
        res = resolvents(c1, c2)
        for i in range(len(res) -1, -1, -1):
            r = res[i].clause
            if(isNil(r)):
                finalClause = res[i]
                print("FOUND NIL, exiting")
                goalFound = True
            
            ## maknuti taut
            if(isTautology(r)):
                res.pop(i)

        ## TODO strategija brisanja, redundantne klauzule

        for r in res:
            sos.append(r)
            # printClause(r)

    printingClauses = [finalClause]
    while(len(printingClauses) != 0):
        printingClause = printingClauses.pop()
        printClause(printingClause)
        for parent in printingClause.parents:
            printingClauses.append(indexedClauses[parent])
        


if __name__ == "__main__":
    main()

