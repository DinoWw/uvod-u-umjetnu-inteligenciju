import argparse
from csv import Error
from heapq import *
from io import TextIOWrapper
from operator import contains
from tracemalloc import start
from typing import Callable, Dict, List, NamedTuple, Optional, Set, Tuple, Union

   

NodeCode = int

class BfsNode(NamedTuple):
   code: NodeCode
   parent: 'Optional[BfsNode]'

class UcsNode(NamedTuple):
   code: NodeCode
   parent: 'Optional[UcsNode]'
   cost: float
   def __lt__(self, other: 'tuple[NodeCode | UcsNode | float | None, ...]') -> bool:
      return self.cost < other.cost

class Transtion(NamedTuple):
   stateTo: NodeCode
   cost: int

class StrTranstion(NamedTuple):
   stateTo: str
   cost: int



def bfs(start: NodeCode, trans: Dict[NodeCode,List[Transtion]], goal: Callable[[NodeCode],bool]) -> Tuple[Optional[BfsNode], int]:
   visitQueue: List[BfsNode] = []
   notedNodes: Set[NodeCode] = set()
   statesVisited: int = 0

   def planToVisit(node: BfsNode):
      visitQueue.append(node)
      notedNodes.add(node.code)
   
   # add start to visitqueue
   planToVisit(BfsNode(start, None))
   
   while(len(visitQueue) != 0):
      # dequeue
      node = visitQueue.pop(0)
      statesVisited += 1
      # check if goal met
      if(goal(node.code)):
         return node, statesVisited
      # queue all neighbors except already noted ones and set parents
      for next in trans[node.code]:
         if (next.stateTo in notedNodes):
            continue
         planToVisit(BfsNode(next.stateTo, node))
      # print("visitQ", [node.code for node in visitQueue])
   
   return None, statesVisited


def insertSortedUcs(el:UcsNode, arr:List[UcsNode]):
   i = 0
   for i in range(len(arr)):
      if( arr[i].cost > el.cost 
         or ( arr[i].cost == el.cost and arr[i].code > el.code ) ):
         arr.insert(i, el)
         return
   arr.append(el)
   


def ucs(start: NodeCode, trans: Dict[NodeCode,List[Transtion]], goal: Callable[[NodeCode],bool]) -> Tuple[Optional[UcsNode], int]:
   visitQueue: List[UcsNode] = []
   notedNodes: Set[NodeCode] = set()
   statesVisited: int = 0

   def planToVisit(node: UcsNode):
      heappush(visitQueue, node)
      # notedNodes.add(node.code)
   
   # add start to visitqueue
   planToVisit(UcsNode(start, None, 0))
   
   while(len(visitQueue) != 0):
      # dequeue
      node = heappop(visitQueue)
      statesVisited += 1
      # check if goal met
      if(goal(node.code)):
         return node, statesVisited
      # queue all neighbors except already noted ones and set parents
      for next in trans[node.code]:
         if (next.stateTo in notedNodes):
            continue
         planToVisit(UcsNode(next.stateTo, node, node.cost + next.cost))
      # print("visitQ", [node.code for node in visitQueue])
   
   return None, statesVisited
         
         
def insertSortedAstar(el:UcsNode, arr:List[UcsNode], heuristic: Dict[NodeCode, float]) -> bool:
   i = 0
   for i in range(len(arr)):
      if( arr[i].cost + heuristic[i] > el.cost + heuristic[el.code] 
         or ( arr[i].cost + heuristic[i] == el.cost + heuristic[el.code] and arr[i].code > el.code ) ):
         arr.insert(i, el)
         return False
   arr.append(el)
   return False
   

def astar(start: NodeCode, trans: Dict[NodeCode,List[Transtion]], goal: Callable[[NodeCode],bool], heuristic: Dict[NodeCode, float]) -> Tuple[Optional[UcsNode], int]:
   visitQueue: List[UcsNode] = []
   minCost: Dict[NodeCode, float] = dict()
   notedNodes: Set[NodeCode] = set()
   statesVisited: int = 0


   def planToVisit(node: UcsNode) -> None:
      err = insertSortedAstar(node, visitQueue, heuristic)
      if(not err) :
         minCost[node.code] = node.cost
      notedNodes.add(node.code)
   
   # add start to visitqueue
   planToVisit(UcsNode(start, None, 0))
   
   while(len(visitQueue) != 0):
      # dequeue
      node = visitQueue.pop(0)
      statesVisited += 1
      # check if goal met
      if(goal(node.code)):
         return node, statesVisited
      # queue all neighbors except already noted ones and set parents
      for next in trans[node.code]:
         if (next.stateTo in notedNodes and minCost[next.stateTo] < node.cost + next.cost):
            continue
         planToVisit(UcsNode(next.stateTo, node, node.cost + next.cost))
      # print("visitQ", [node.code for node in visitQueue])
   
   return None, statesVisited
         

def loadNextLine(buffer: TextIOWrapper) -> str:
   while True:
      line = buffer.readline()
      if not line.startswith("#") :
         return line

def parseInputDataFromFile(filename: str) -> Tuple[str, List[str], Dict[str, List[StrTranstion]]]:
   f = open(filename)
   startState = loadNextLine(f).strip()
   goalStates = loadNextLine(f).strip().split(" ")
   transitions: Dict[str,List[StrTranstion]] = {}
   while True :
      line = loadNextLine(f).strip(" \n")
      if (line == ""):
         break
      p = line.split(":")
      transitions[p[0]] = []
      if(p[1] == ""):
         strTransitions: List[str] = []
      else:
         strTransitions = p[1].strip().split(" ")
      for strTransition in strTransitions:
         pair = strTransition.split(",")
         transitions[p[0]].append( StrTranstion( pair[0], int(pair[1]) ) )

   f.close()
   return startState, goalStates, transitions

def enumerateStates(startStateStr: str, goalStatesStr: List[str], transitionsStr: Dict[str,List[StrTranstion]]) \
   -> Tuple[NodeCode, List[NodeCode], Dict[NodeCode,List[Transtion]], Dict[NodeCode, str], Dict[str, NodeCode]]:

   # collect states
   states: Set[str] = set()
   states.add(startStateStr)
   for state in goalStatesStr:
      states.add(state)
   for stateFrom, nexts in transitionsStr.items():
      states.add(stateFrom)
      for next in nexts:
         states.add(next.stateTo)

   # sort states
   stateList: List[str] = sorted(states)

   # enumerate states by sorted order
   stateDict: Dict[str, int] = {}
   lookupDict: Dict[int, str] = {}
   stateId: NodeCode = 0
   for state in stateList:
      stateDict[state] = stateId
      lookupDict[stateId] = state
      stateId += 1

   # regenerate transitions
   nodeTransitions: Dict[NodeCode,List[Transtion]] = {}
   for stateFrom, nexts in transitionsStr.items():
      def sortF(t: Transtion) -> int:
         return t.stateTo
      nodeTransitions[stateDict[stateFrom]] = sorted([Transtion( stateDict[next.stateTo], next.cost ) for next in nexts], key=sortF)

   # return 
   return stateDict[startStateStr], [stateDict[state] for state in goalStatesStr], nodeTransitions, lookupDict, stateDict

def goalFunctionGenerator(goalStates: List[NodeCode]):
   def goalFunction(code: NodeCode) -> bool:
      return goalStates.count(code) != 0
   
   return goalFunction

def getPathTo(node: Optional[Union[BfsNode, UcsNode]]) -> List[Union[BfsNode, UcsNode]]:
   nodeList: List[Union[BfsNode, UcsNode]] = []
   while(node is not None):
      nodeList.append(node)
      node = node.parent
   nodeList.reverse()
   return nodeList

def parseHeuristicFromFile(filename: str) -> Dict[str, float]:
   f = open(filename)

   heuristicStr: Dict[str, float] = {}

   while True :
      line = loadNextLine(f).strip(" \n")
      if (line == ""):
         break
      p = line.split(": ")
      heuristicStr[p[0]] = int(p[1])

   f.close()
   return heuristicStr

def printOutput(endNode: Union[None, BfsNode, UcsNode], statesVisited: int, path: List[str], cost: float):
   print(f"[FOUND_SOLUTION]: {'yes' if endNode is not None else 'no'}")
   print(f"[STATES_VISITED]: {statesVisited}")
   print(f"[PATH_LENGTH]: {len(path)}")
   print(f"[TOTAL_COST]: {float(cost)}")
   print(f"[PATH]: {path[0]}", end='')
   for i in range(1, len(path)):
      print(f" => {path[i]}", end="")
   print()


def enumerateHeuristic(heuristicStr: Dict[str, float], strToNodeCode: Dict[str, NodeCode]) -> Dict[NodeCode, float]:
   heuristic: Dict[NodeCode, float] = {}

   for node, weight in heuristicStr.items():
      heuristic[strToNodeCode[node]] = weight

   return heuristic


def checkConsistent(start: NodeCode, trans: Dict[NodeCode,List[Transtion]], goal: Callable[[NodeCode],bool], heuristic: Dict[NodeCode, float], stateLookup: Dict[NodeCode, str])-> bool:
   isConsistent = True
   for state1, transitionList in transitions.items():
      for transition in transitionList:
         h1 = heuristic[state1]
         state2 = transition.stateTo
         h2 = heuristic[state2]
         c = transition.cost
         ok = h1 <= h2 + c
         isConsistent = isConsistent and ok
         print(f"[CONDITION]: [{'OK' if ok else 'ERR'}] h({stateLookup[state1]}) <= h({stateLookup[state2]}) + c: {float(h1)} <= {float(h2)} + {float(c)}")
   return isConsistent

def checkOptimistic(trans: Dict[NodeCode,List[Transtion]], goal: Callable[[NodeCode],bool], heuristic: Dict[NodeCode, float], stateLookup: Dict[NodeCode, str])-> bool:
   
   allNodes:List[NodeCode] = list(trans.keys())
   idealHeuristic: Dict[NodeCode, float] = dict()
   
   for startNode in allNodes:
      # UCS 
      endNode, _ = ucs(startNode, trans, goal)

      if( endNode is None ):
         print("Error()")
         break

      idealHeuristic[startNode] = endNode.cost

   # for startNode in allNodes:
   #    if(goal(startNode)):
   #       idealHeuristic[startNode] = 0
   #    if startNode in idealHeuristic:
   #       continue

   #    # UCS 
   #    endNode, _ = ucs(startNode, trans, goalF)

   #    if( endNode is None):
   #       print("Error()")
   #       break

   #    path: List[UcsNode] = getPathTo(endNode)   # type: ignore

   #    if(endNode.code not in idealHeuristic) :
   #       idealHeuristic[endNode.code] = 0

   #    for pathNode in path:
   #       idealHeuristic[pathNode.code] = endNode.cost - pathNode.cost + idealHeuristic[endNode.code]
   #       goalNodes.add(pathNode.code)

   allGood = True
   for node, h1 in heuristic.items():
      h2 = idealHeuristic[node]
      ok = h1 <= h2
      allGood = allGood and ok
      print(f"[CONDITION]: [{'OK' if ok else 'ERR'}] h({stateLookup[node]}) <= h*: {float(h1)} <= {float(h2)}")
      
   return allGood




if __name__ == "__main__":
      

   parser = argparse.ArgumentParser(
      prog="ooup-lab1"
   )
   parser.add_argument("--alg", choices=['bfs', 'ucs', 'astar'], help="kratica za algoritam za pretraˇzivanje (vrijednosti: bfs, ucs, ili astar)")
   parser.add_argument("--ss", help="putanja do opisnika prostora stanja")
   parser.add_argument("--h", help="putanja do opisnika heuristike")
   parser.add_argument("--check-consistent", action="store_true", help="zastavica koja signalizira da se za danu heuristiku zeli provjeriti optimisticnost")
   parser.add_argument("--check-optimistic", action="store_true", help="zastavica koja signalizira da se za danu heuristiku zeli provjeriti konzistentnost")

   flags = parser.parse_args()


   startStateStr, goalStatesStr, transitionsStr = parseInputDataFromFile(flags.ss)
   startState, goalStates, transitions, lookupTable, reverseLookupTable = enumerateStates(startStateStr, goalStatesStr, transitionsStr)
   goalFunction = goalFunctionGenerator(goalStates)
   
   if(flags.alg == "bfs"):
      
      endNode, statesVisited = bfs(startState, transitions, goalFunction)

      # if(endNode is None):
      #    pass
      
      # print(lookupTable[startState])
      # print(goalStates)

      path: List[str] = [lookupTable[node.code] for node in getPathTo(endNode)]

      print("# BFS")
      printOutput(endNode, statesVisited, path, float(-1))

   
   elif(flags.alg == "ucs"):

      endNode, statesVisited = ucs(startState, transitions, goalFunction)

      path: List[str] = [lookupTable[node.code] for node in getPathTo(endNode)]

      print("# UCS")
      printOutput(endNode, statesVisited, path, float( endNode.cost if endNode is not None else -1 ))

   elif(flags.alg == "astar"):
      heuristicStr: Dict[str, float] = parseHeuristicFromFile(flags.h)
      heuristic: Dict[NodeCode, float] = enumerateHeuristic(heuristicStr, reverseLookupTable)

      endNode, statesVisited = astar(startState, transitions, goalFunction, heuristic)

      path: List[str] = [lookupTable[node.code] for node in getPathTo(endNode)]

      print(f"# A-STAR {flags.h}")
      printOutput(endNode, statesVisited, path, float( endNode.cost if endNode is not None else -1 ))


   if(flags.check_consistent):
      heuristicStr: Dict[str, float] = parseHeuristicFromFile(flags.h)
      heuristic: Dict[NodeCode, float] = enumerateHeuristic(heuristicStr, reverseLookupTable)

      print(f"# HEURISTIC-CONSISTENT {flags.h}")

      isConsistent = checkConsistent(startState, transitions, goalFunction, heuristic, lookupTable)

      print(f"[CONCLUSION]: Heuristic is {'' if isConsistent else 'not '}consistent.")
   
   elif(flags.check_optimistic):
      heuristicStr: Dict[str, float] = parseHeuristicFromFile(flags.h)
      heuristic: Dict[NodeCode, float] = enumerateHeuristic(heuristicStr, reverseLookupTable)

      print(f"# HEURISTIC-OPTIMISTIC {flags.h}")

      isOptimistic = checkOptimistic(transitions, goalFunction, heuristic, lookupTable)

      print(f"[CONCLUSION]: Heuristic is {'' if isOptimistic else 'not '}optimistic.")



