import sys
from collections import defaultdict
from functools import reduce
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
    freeCombs[newClause.id] = {i for i in range(0, newClause.id) if i not in bannedClauses}

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

def clauseStr(clause: Clause) -> str:
    clauseList = list(clause.clause)
    return f"{clauseList[0]}{reduce(lambda s, l : s + ' v ' + formatLiteral(l), clauseList[1:], '')}"

def formatLiteral(literal: Literal):
    return f"{'~' if literal.negated else ''}{literal.name}"

def isNil(clause: CNF):
    return len( clause ) == 0

def isContainedIn(c1: Clause, c2: Clause) -> bool:
    return c1.clause.issubset(c2.clause)

def hideRedundant(c1: Clause, c2: Clause) -> None:
    if(c1.id == c2.id):
        return
    if ( isContainedIn(c1, c2) ):
        hideClause(c2.id)
    elif ( isContainedIn(c2, c1) ):
        hideClause(c1.id)

def hideRedundants(c1: Clause, clauses: List[Clause]):
    for clause in clauses:
        hideRedundant(clause, c1)

bannedClauses: Set[int] = set()
def hideClause(id: int):
    bannedClauses.add(id)
    for i, clauses in freeCombs.items():
        if(id in clauses):
            clauses.remove(id)
            if(len(clauses) == 0):
                del freeCombs[i]
    if(id in freeCombs):
        del freeCombs[id]

pickedPairs: Dict[int, Set[int]] = defaultdict(Set[int])
def pickClauses(original: List[Clause], sos: List[Clause]):
    if( len( freeCombs.keys()) == 0 ):
        print(f"[CONCLUSION]: {clauseStr(goalClause)} is unknown") # type: ignore
        exit(0)

    index1 = random.choice(list(freeCombs.keys()))
    index2 = freeCombs[index1].pop()

    if ( len( freeCombs[index1] ) == 0 ):
        del freeCombs[index1]

    if(index2 < len(original)):
        ca = original[index2]
    else:
        ca = sos[index2 - len(original)]
    return ca, sos[index1 - len(original)]
    



goalClause = None
def main() :
    if (len(sys.argv) != 3):
        raise ValueError("supply alg and filename as arguments")
    alg = sys.argv[1]
    filename = sys.argv[2]
    
    clauses: List[Clause] = parseInputData(filename)

    global goalClause
    goalClause = clauses.pop()
    indexedClauses.pop()    # the original goal clause should never be referenced, only its negations from sos
    del freeCombs[goalClause.id]
    global clauseCounter
    clauseCounter -= 1

    for clause in clauses:
        printClause(clause)
    print("GOAL: ", end="")
    printClause(goalClause)

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
                break
            
            ## maknuti taut
            if(isTautology(r)):
                res.pop(i)
                continue

            ## maknuti redundantne
            hideRedundants(res[i], clauses + sos + res)

        ## TODO strategija brisanja, redundantne klauzule

        for r in res:
            sos.append(r)
            # printClause(r)

    printingClauses = [finalClause] # type: ignore
    while(len(printingClauses) != 0):
        printingClause = printingClauses.pop()
        printClause(printingClause)
        for parent in printingClause.parents:
            printingClauses.append(indexedClauses[parent])

    print(f"[CONCLUSION]: {clauseStr(goalClause)} is true")
        


if __name__ == "__main__":
    main()

