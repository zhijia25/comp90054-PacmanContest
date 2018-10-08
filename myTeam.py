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
    self.home = gameState.getAgentPosition(self.index)
    self.originalFood=len(self.getFood(gameState).asList())
    self.thisDenfending=self.originalFood
    self.walls = gameState.getWalls().asList()
    self.foodAccumulate=0
    self.eatenFood=None
    self.earn=0








  def simpleHeuristic(self,gameState,goal):


    if goal==None:
      return 0
    heuristic = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), goal)
    return heuristic


  def enemyConcernHeuristic(self,gameState,enemyDefenders,goal):

    if goal==None:
      return 0
    if len(enemyDefenders)>0:
        heuristic = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), goal) + 100000 * min(
      [self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), defender.getPosition()) for defender in enemyDefenders])
    else:
      heuristic = self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), goal)
    return  heuristic

  def getSuccessor(self, gameState, action):
    """
    Finds the next successor which is a grid position (location tuple).
    """
    successor = gameState.generateSuccessor(self.index, action)
    pos = successor.getAgentState(self.index).getPosition()
    if pos != nearestPoint(pos):
      # Only half a grid position was covered
      return successor.generateSuccessor(self.index, action)
    else:
      return successor


  def getSuccessors(self, currentPosition, gameState):
    successors = []
    forbidden = copy.deepcopy(self.walls)
    if gameState.getAgentState(self.index).isPacman:
      enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
      defenders = [a for a in enemies if not a.isPacman and a.getPosition() != None and a.scaredTimer <= 0]
      if len(defenders) > 0:
        defendersCoordinate = [i.getPosition() for i in defenders]
        forbidden=forbidden+defendersCoordinate
    for action in [Directions.NORTH, Directions.SOUTH, Directions.EAST, Directions.WEST]:
      x, y = currentPosition
      dx, dy = Actions.directionToVector(action)
      nextx, nexty = int(x + dx), int(y + dy)
      if (nextx, nexty) not in forbidden:
        nextPosition = (nextx, nexty)
        successors.append((nextPosition, action))
    return successors

  def aStarSearch(self, goal,heuristic):
    start =self.getCurrentObservation().getAgentPosition(self.index)
    openSet = util.PriorityQueue()
    openSet.push(( start,  []), 0)
    visitedNodes = []
    gameState=self.getCurrentObservation()

    if goal is None:
      self.eatenFood=None
      middleLine = [(gameState.data.layout.width / 2, y) for y in range(0, gameState.data.layout.height)]
      availableMiddle = [a for a in middleLine if a not in self.walls]
      middleDis = [self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), middle) for middle in
                   availableMiddle]
      closeMiddle = [m for m, d in zip(availableMiddle, middleDis) if d == min(middleDis)]

      goal = random.choice(closeMiddle)
      if gameState.getAgentState(self.index).getPosition() == goal:
        return Directions.EAST
      return self.aStarSearch(goal, self.simpleHeuristic(gameState, goal))

    while (openSet.isEmpty() == False):

      currentPosition, trace = openSet.pop()

      if currentPosition in visitedNodes:
        continue
      visitedNodes.append(currentPosition)

      if currentPosition == goal:
        if len(trace)==0:

          return Directions.STOP
        return trace[0]
      successors = self.getSuccessors(currentPosition, self.getCurrentObservation())
      for successor in successors:
        cost = len(trace + [successor[1]])+heuristic
        openSet.push((successor[0], trace + [successor[1]]), cost)
    return Directions.STOP



class Attacker(ReflexCaptureAgent):


  def chooseAction(self,gameState):

    actions = [i for i in gameState.getLegalActions(self.index) if i != Directions.STOP]
    foods=[food for food in self.getFood(gameState).asList()]
    foodDistance=[self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),a) for a in foods]
    closeFood = [f for f, d in zip(foods, foodDistance) if d == min(foodDistance)]
    values = [self.evaluate(gameState, a) for a in actions]
    maxValue = max(values)
    bestActions = [a for a, v in zip(actions, values) if v == maxValue]
    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    enemyDefenders= [a for a in enemies if a.getPosition() != None ]
    enemyPosition=[e.getPosition() for e in enemyDefenders]
    middleLine = [(gameState.data.layout.width / 2, y) for y in range(0, gameState.data.layout.height)]
    availableMiddle = [a for a in middleLine if a not in self.walls]
    middleDis = [self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), middle) for middle in
                 availableMiddle]
    closeMiddle = [m for m, d in zip(availableMiddle, middleDis) if d == min(middleDis)]
    back = closeMiddle[0]
    for o in self.getOpponents(gameState):
      if gameState.getAgentState(o).scaredTimer > 0:
        print 'scared'
        return self.aStarSearch(closeFood[0], self.simpleHeuristic(gameState, closeFood[0]))

    if not gameState.getAgentState(self.index).isPacman:
      return self.aStarSearch(closeFood[0],self.enemyConcernHeuristic(gameState, enemyDefenders, closeFood[0]))

    if len(self.getCapsules(gameState)) is not 0:
      capsuleDis=[self.getMazeDistance(gameState.getAgentState(self.index).getPosition(),c) for c in self.getCapsules(gameState)]
      closeCapsules=[c for c,d in zip(self.getCapsules(gameState),capsuleDis) if d==min(capsuleDis)]

      if len(enemyDefenders)  > 0:
        if len(closeCapsules) is not 0:
          print 'chasen,eat capsule'
          return self.aStarSearch(closeCapsules[0], self.enemyConcernHeuristic(gameState,enemyDefenders,closeCapsules[0]))
        else:
          return self.aStarSearch(back,self.enemyConcernHeuristic(gameState, enemyDefenders, back))
      else:
        if gameState.getAgentState(self.index).numCarrying > 15:
          print 'enough,back'
          return self.aStarSearch(back, self.enemyConcernHeuristic(gameState, enemyDefenders, back))
        else:
          print 'normal eat'

          return self.aStarSearch(closeFood[0], self.enemyConcernHeuristic(gameState, enemyDefenders, closeFood[0]))
    else:
      if len(enemyDefenders) > 0:
        if gameState.getAgentState(self.index).numCarrying == 0:
          return  self.aStarSearch(closeFood[0],self.enemyConcernHeuristic(gameState, enemyDefenders, closeFood[0]))
        if gameState.getAgentState(self.index).numCarrying > 0:
          print 'chasen,has food,back'
          return self.aStarSearch(back, self.enemyConcernHeuristic(gameState,enemyDefenders,  back))
        else:
          print 'chasen,no food, eat'
          return self.aStarSearch(closeFood[0],self.enemyConcernHeuristic(gameState, enemyDefenders, closeFood[0]))
      else:
        if gameState.getAgentState(self.index).numCarrying > 15:
          print 'enough, no capsule, back'
          return self.aStarSearch(back, self.enemyConcernHeuristic(gameState, enemyDefenders, back))
        else:
          print 'normal eat,no calsule'
          return self.aStarSearch(closeFood[0], self.enemyConcernHeuristic(gameState, enemyDefenders, closeFood[0]))













  def getFeatures(self,gameState, action):
    features=util.Counter()
    successor=self.getSuccessor(gameState,action)
    foodList = self.getFood(successor).asList()
    features['successorScore'] = -len(foodList)  #
    features['mightBeChasen']=0
    if self.getOpponents(successor)==0:
      features['mightBeChasen']=1


    if len(self.getFood(gameState).asList()) > 0:
      myPos = successor.getAgentState(self.index).getPosition()
      minDistance = min([self.getMazeDistance(myPos, food) for food in self.getFood(successor).asList()])
      features['distanceToFood' ] = minDistance

    return  features

  def getWeights(self, gameState, action):
    return {'mightBeChasen': -50, 'distanceToFood' :-1,'successorScore': 100, }


  def evaluate(self,gameState, action):
    features = self.getFeatures(gameState, action)
    weights = self.getWeights(gameState, action)
    return features * weights



class Defender(ReflexCaptureAgent):





  def isEaten(self):

    if self.getPreviousObservation() is not None:
      if len(self.getFoodYouAreDefending(self.getCurrentObservation()).asList())<len(self.getFoodYouAreDefending(self.getPreviousObservation()).asList()):
        return True
    else:
      return  False

  def getEaten(self):
    defendLeft=self.getFoodYouAreDefending(self.getCurrentObservation()).asList()
    lastDefend=self.getFoodYouAreDefending(self.getPreviousObservation()).asList()
    eaten=[left for left in lastDefend if left not in defendLeft]
    eatenDis=[self.getMazeDistance(self.getCurrentObservation().getAgentState(self.index).getPosition(),eat) for eat in eaten]
    closeEaten=[e for e ,d in zip(eaten,eatenDis) if d==min(eatenDis)]

    self.eatenFood=closeEaten[0]
    return closeEaten[0]


  def beginEaten(self):
    if len(self.getFoodYouAreDefending(self.getCurrentObservation()).asList())<self.thisDenfending:
      return  True
    else:
      return False







  def chooseAction(self, gameState):

    enemies = [gameState.getAgentState(i) for i in self.getOpponents(gameState)]
    invaders = [a for a in enemies if a.isPacman and a.getPosition() != None]
    for index in self.getOpponents(gameState):
      if self.getPreviousObservation() is not None:
        if gameState.getAgentState(index).numReturned>self.getPreviousObservation().getAgentState(index).numReturned:

          self.thisDenfending=self.thisDenfending-( gameState.getAgentState(index).numReturned-self.getPreviousObservation().getAgentState(index).numReturned)

    if len(invaders) != 0:
      invadersDis = [self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), a.getPosition()) for a in
                     invaders]
      minDIs = min(invadersDis)
      target = [a for a, v in zip(invaders, invadersDis) if v == minDIs]
      return self.aStarSearch(random.choice(target).getPosition(),
                              self.simpleHeuristic(gameState, random.choice(target).getPosition()))
    if self.beginEaten():

      if self.isEaten():

        return self.aStarSearch(self.getEaten(), self.simpleHeuristic(gameState, self.getEaten()))
      else:

        return self.aStarSearch(self.eatenFood,self.simpleHeuristic(gameState, self.eatenFood))


    else:

      middleLine = [(gameState.data.layout.width / 2, y) for y in range(0, gameState.data.layout.height)]
      availableMiddle = [a for a in middleLine if a not in self.walls]
      middleDis = [self.getMazeDistance(gameState.getAgentState(self.index).getPosition(), middle) for middle in
                   availableMiddle]
      closeMiddle = [m for m, d in zip(availableMiddle, middleDis) if d == min(middleDis)]
      goal = closeMiddle[0]
      if gameState.getAgentState(self.index).getPosition() == goal:
        return Directions.STOP
      return self.aStarSearch(goal, self.simpleHeuristic(gameState, goal))




















