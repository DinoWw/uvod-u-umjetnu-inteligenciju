import argparse
from io import TextIOWrapper
from typing import Callable, Dict, List, NamedTuple, Optional, Set, Tuple

   
   

NodeCode = int
# Node = dict[str,NodeCode]#dict{"code":NodeCode, "parent":Node}

class Node:
   code: NodeCode
   parent: 'Optional[Node]'
   def __init__(self, code_: NodeCode, parent_: 'Optional[Node]'): 
      self.code = code_
      self.parent = parent_

class Transtion(NamedTuple):
   stateTo: NodeCode
   cost: int

class StrTranstion(NamedTuple):
   stateTo: str
   cost: int


visitQueue: List[Node] = []
notedNodes: Set[NodeCode] = set()
def bfs(start: NodeCode, trans: Dict[NodeCode,List[Transtion]], goal: Callable[[NodeCode],bool]) -> Optional[Node]:
   # add start to visitqueue
   visitQueue.append(Node(start, None))
   
   while(len(visitQueue) != 0):
      # dequeue
      node = visitQueue.pop(0)   
      # check if goal met
      if(goal(node.code)):
         return node   
      # note dequeueued node
      notedNodes.add(node.code)
      # queue all neighbors except already noted ones and set parents
      for next in trans[node.code]:
         if (next.stateTo in notedNodes):
            continue
         visitQueue.append(Node(next.stateTo, node))
         

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

   return startState, goalStates, transitions

def enumerateStates(startStateStr: str, goalStatesStr: List[str], transitionsStr: Dict[str,List[StrTranstion]]) -> Tuple[NodeCode, List[NodeCode], Dict[NodeCode,List[Transtion]], Dict[NodeCode, str]]:

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
      nodeTransitions[stateDict[stateFrom]] = [Transtion( stateDict[next.stateTo], next.cost ) for next in nexts]

   # return 
   return stateDict[startStateStr], [stateDict[state] for state in goalStatesStr], nodeTransitions, lookupDict

def goalFunctionGenerator(goalStates: List[NodeCode]):
   def goalFunction(code: NodeCode) -> bool:
      return goalStates.count(code) != 0
   
   return goalFunction

def getPathTo(node: Optional[Node]) -> List[Node]:
   nodeList: List[Node] = []
   while(node is not None):
      nodeList.append(node)
      node = node.parent
   nodeList.reverse()
   return nodeList


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
   
   if(flags.alg == "bfs"):
      startStateStr, goalStatesStr, transitionsStr = parseInputDataFromFile(flags.ss)
      startState, goalStates, transitions, lookupTable = enumerateStates(startStateStr, goalStatesStr, transitionsStr)
      
      # print(startStateStr)
      # print(startState)
      # print(goalStatesStr)
      # print(goalStates)
      # print(transitionsStr)
      # print(transitions)
      # print(lookupTable)

      # TODO: sort list of statesTo in transtions if need be

      goalFunction = goalFunctionGenerator(goalStates)
      
      endNode = bfs(startState, transitions, goalFunction)

      if(endNode is None):
         pass
      
      print(lookupTable[startState])
      print(goalStates)
      print([lookupTable[node.code] for node in getPathTo(endNode)])
      