# myTeam.py
# ---------
# Licensing Information:  You are free to use or extend these projects for
# educational purposes provided that (1) you do not distribute or publish
# solutions, (2) you retain this notice, and (3) you provide clear
# attribution to UC Berkeley, including a link to http://ai.berkeley.edu.
# 
# Attribution Information: The Pacman AI projects were developed at UC Berkeley.
# The core projects and autograders were primarily created by John DeNero
# (denero@cs.berkeley.edu) and Dan Klein (klein@cs.berkeley.edu).
# Student side autograding was added by Brad Miller, Nick Hay, and
# Pieter Abbeel (pabbeel@cs.berkeley.edu).


from captureAgents import CaptureAgent
import random, time, util
import math
from game import Directions,Actions
import  copy
import game
from util import nearestPoint

#################
# Team creation #
#################

def createTeam(firstIndex, secondIndex, isRed,
               first = 'Attacker', second = 'Defender'):
  """
  This function should return a list of two agents that will form the
  team, initialized using firstIndex and secondIndex as their agent
  index numbers.  isRed is True if the red team is being created, and
  will be False if the blue team is being created.

  As a potentially helpful development aid, this function can take
  additional string-valued keyword arguments ("first" and "second" are
  such arguments in the case of this function), which will come from
  the --redOpts and --blueOpts command-line arguments to capture.py.
  For the nightly contest, however, your team will be created without
  any extra arguments, so you should make sure that the default
  behavior is what you want for the nightly contest.
  """

  # The following line is an example only; feel free to change it.
  return [eval(first)(firstIndex), eval(second)(secondIndex)]

##########
# Agents #
##########

class ReflexCaptureAgent(CaptureAgent):
  """
  A Dummy agent to serve as an example of the necessary agent structure.
  You should look at baselineTeam.py for more details about how to
  create an agent as this is the bare minimum.
  """

  def registerInitialState(self, gameState):
    """
    This method handles the initial setup of the
    agent to populate useful fields (such as what team
    we're on).

    A distanceCalculator instance caches the maze distances
    between each pair of positions, so your agents can use:
    self.distancer.getDistance(p1, p2)

    IMPORTANT: This method may run for at most 15 seconds.
    """



    CaptureAgent.registerInitialState(self, gameState)
    self.home = gameState.getAgentState(self.index).getPosition()
    self.originalFood=len(self.getFood(gameState).asList())
    self.defendFood=len(self.getFoodYouAreDefending(gameState).asList())
    self.walls = gameState.getWalls().asList()
    self.lastEaten=None
    self.eatenFood=None


  def getMiddleLines(self,gameState):
    if self.red:
      middleLine = [((gameState.data.layout.width / 2) - 1, y) for y in range(0, gameState.data.layout.height)]
    else:
      middleLine = [(gameState.data.layout.width / 2, y) for y in range(0, gameState.data.layout.height)]
    availableMiddle = [a for a in middleLine if a not in self.walls]
    return availableMiddle


  def getInvaders(self, gameState):
    enemies = [gameState.getAgentState(o) for o in self.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    if len(invaders)==0:
      return None
    else:
      return invaders

  def getDefenders(self,gameState):
    enemies=[gameState.getAgentState(o) for o in self.getOpponents(gameState)]
    defenders=[a for a in enemies if a.getPosition() != None and not a.isPacman]
    if len(defenders)==0:
      return  None
    else:
      return defenders


  def getCloseFood(self, gameState):
    foods = [food for food in self.getFood(gameState).asList()]
    foodDistance = [self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), a) for a in foods]
    closeFood = [f for f, d in zip(foods, foodDistance) if d == min(foodDistance)]
    if len(closeFood)==0:
      return None
    else:
      return closeFood[0]

  def getcloseCapsule(self,gameState):
    capsules = self.getCapsules(gameState)
    if len(capsules)==0:
      return None
    else:
      capsuleDis = [self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), c) for c in capsules]
      closeCapsules=[c for c,d in zip(self.getCapsules(gameState),capsuleDis) if d==min(capsuleDis)]
      return closeCapsules[0]




  def getSuccessor(self, gameState, action):
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor

  def getSuccessors(self, currentPosition):
    successors = []
    forbidden =self.walls
    for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = currentPosition
      dx, dy = Actions.directionToVector(action)
      nextx, nexty = int(x + dx), int(y + dy)
      if (nextx, nexty) not in forbidden:
        nextPosition = (nextx, nexty)
        successors.append((nextPosition, action))
    return successors


  def simpleHeuristic(self,gameState,thisPosition):
    return 0

  def enemyConcernHeuristic(self,gameState,thisPosition):
     heuristics=[]
     ghoasts=self.getDefenders(gameState)
     if ghoasts==None :
       return 0
     else:
       for o in ghoasts:
        if self.getMazeDistance(thisPosition,o.getPosition())<3:
          d=self.getMazeDistance(thisPosition,o.getPosition())
          heuristics.append(math.pow((d-5),4))
        else:
          heuristics.append(0)
       print max(heuristics)
       return max(heuristics)


  def aStarSearch(self,gameState,goal,heuristic):
    start =self.getCurrentObservation().getAgentState(self.index).getPosition()
    openSet = util.PriorityQueue()
    openSet.push(( start,[]), 0)
    visitedNodes = []
    while not openSet.isEmpty():
      node,trace=openSet.pop()
      if node == goal:
        if len(trace)==0:
          return 'Stop'

        return trace[0]
      if node not in visitedNodes:
        visitedNodes.append(node)
        successors=self.getSuccessors(node)
        for successor in successors:
          cost= len(trace +[successor[1]])+heuristic(gameState,successor[0])
          if successor not in visitedNodes:
            openSet.push((successor[0], trace + [successor[1]]), cost)
    if goal != self.home:
      return self.aStarSearch(gameState,self.home,self.enemyConcernHeuristic)
    return 'Stop'


class Attacker(ReflexCaptureAgent):

  def chooseAction(self,gameState):

    closeCapsule=self.getcloseCapsule(gameState)
    foods=self.getFood(gameState).asList()
    closeFood=self.getCloseFood(gameState)
    middleLines = self.getMiddleLines(gameState)
    middleDis = [self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), mi) for mi in
                 middleLines]
    closeMiddle = [m for m, d in zip(middleLines, middleDis) if d == min(middleDis)]
    middle = closeMiddle[0]
    defenders = self.getDefenders(gameState)
    print self.getDefenders(gameState)
    invaders=self.getInvaders(gameState)


    if gameState.getAgentState(self.index).scaredTimer > 0 and invaders != None and not gameState.getAgentState(self.index).isPacman:
      for invader in invaders:
        if self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),
                                invader.getPosition()) <= 2:
          return self.aStarSearch(gameState, self.home, self.enemyConcernHeuristic)

    if self.getScore(gameState)<0:
      if gameState.getAgentState(self.index).numCarrying +self.getScore(gameState)>0:
        return self.aStarSearch(gameState, middle, self.enemyConcernHeuristic)
      if gameState.getAgentState(self.index).numCarrying>10:
        return self.aStarSearch(gameState, middle, self.enemyConcernHeuristic)

    if gameState.data.timeleft<200 or len(foods)<3 or gameState.getAgentState(self.index).numCarrying >28:
      if gameState.getAgentState(self.index).numCarrying>0:
        print 'go home, nearly end'
        return self.aStarSearch(gameState,middle,self.enemyConcernHeuristic)



    if defenders!=None:
      for defender in defenders:
        if defender.scaredTimer >0:
          if defender.scaredTimer > 10:
            return self.aStarSearch(gameState,closeFood,self.simpleHeuristic)
          else:
            return self.aStarSearch(gameState, closeFood, self.enemyConcernHeuristic)

    if closeCapsule!=None:
      if defenders!=None:
       for d in defenders:
         if self.getMazeDistance(d.getPosition(),closeCapsule)<2:
           print 'enemy close to cap,back'
           return self.aStarSearch(gameState, middle, self.enemyConcernHeuristic)
       print 'eat cap'
       return self.aStarSearch(gameState,closeCapsule,self.enemyConcernHeuristic)

    if closeCapsule==None:
      if defenders!=None and gameState.getAgentState(self.index).numCarrying !=0:
        print 'chasen,back'
        return self.aStarSearch(gameState,middle,self.enemyConcernHeuristic)

    print 'normal eat'
    return self.aStarSearch(gameState,closeFood,self.enemyConcernHeuristic)


###########################################################################################################################################################################################################################################
class Defender(ReflexCaptureAgent):

  def isEating(self):
    if self.getPreviousObservation() is not None and len(self.getFoodYouAreDefending(self.getCurrentObservation()).asList())<len(self.getFoodYouAreDefending(self.getPreviousObservation()).asList()):
        return True
    else:
      return  False

  def setEaten(self,eaten):
    self.eatenFood=eaten

  def getEaten(self):
    defendLeft=self.getFoodYouAreDefending(self.getCurrentObservation()).asList()
    lastDefend=self.getFoodYouAreDefending(self.getPreviousObservation()).asList()
    eaten=[left for left in lastDefend if left not in defendLeft]
    eatenDis=[self.getMazeDistance(self.getCurrentObservation().getAgentState(self.index).getPosition(),eat) for eat in eaten]
    closeEaten=[e for e ,d in zip(eaten,eatenDis) if d==min(eatenDis)]
    self.setEaten(closeEaten[0])
    return closeEaten[0]


  def beginEaten(self):
    if len(self.getFoodYouAreDefending(self.getCurrentObservation()).asList())<self.defendFood:
      return True
    else:
      return False

  def chooseAction(self, gameState):
    invaders=self.getInvaders(gameState)

    middleLines = self.getMiddleLines(gameState)
    middleDis = [self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), mi) for mi in
                 middleLines]
    closeMiddle = [m for m, d in zip(middleLines, middleDis) if d == min(middleDis)]
    middle = closeMiddle[0]
    for index in self.getOpponents(gameState):
      if self.getPreviousObservation() is not None:
        if gameState.getAgentState(index).numReturned>self.getPreviousObservation().getAgentState(index).numReturned:
          self.defendFood=self.defendFood-( gameState.getAgentState(index).numReturned-self.getPreviousObservation().getAgentState(index).numReturned)

    if gameState.getAgentState(self.index).getPosition()==middle or gameState.getAgentState(self.index).getPosition()==self.eatenFood:
      return self.aStarSearch(gameState,self.home,self.simpleHeuristic)

    if gameState.getAgentState(self.index).scaredTimer>0 and invaders!=None:
      for invader in invaders:
         if self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),
                                invader.getPosition()) <= 2:
           return self.aStarSearch(gameState,self.home, self.enemyConcernHeuristic)

    if invaders!=None:
      invadersDis = [self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), a.getPosition()) for a in
                     invaders]
      minDIs = min(invadersDis)
      target = [a.getPosition() for a, v in zip(invaders, invadersDis) if v == minDIs]
      return self.aStarSearch(gameState,target[0],self.simpleHeuristic)

    if self.beginEaten():
      if self.isEating():
        eaten=self.getEaten()
        self.setEaten(eaten)
        return self.aStarSearch(gameState,eaten,self.simpleHeuristic)
      else:
        return self.aStarSearch(gameState,self.eatenFood,self.simpleHeuristic)

    return self.aStarSearch(gameState,middle,self.simpleHeuristic)























