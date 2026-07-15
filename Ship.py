import re
from Container import Container
import copy
from Node import Node
import heapq

class Ship:
    def __init__(self, manifest_file):
        self.R = 8
        self.C = 12
        self.manifest_file = manifest_file
        
        # data structures
        self.containers = []
        # 0 might have significantce - empty crate here vs just air i dont remember
        self.grid = [[None for _ in range(self.C)] for _ in range(self.R)]
        self.loadedCrane = None
        #Crane begin position 1,8 (r,c)
        self.craneRestR = 8
        self.craneRestC = 0
        
        self.cranePosR = self.craneRestR
        self.cranePosC = self.craneRestC

        self.max_weight = 0


    # create manifest method
    # i believe that this is the object that is deep copied in A star, so do not read from manifest file in init
    def read_manifest(self):
        try:
            with open(self.manifest_file, 'r') as f:
                lines = f.read()
        except FileNotFoundError:
            print(self.manifest_file + " not found")
            return
        
        # regex for extracting info from each line
        # capture group for row#, col#, weight, desc
        # [01,02], {00120}, Walmart Ohio 1000 air fryers
        regex = r"\[(\d{2}),(\d{2})\]\s*,\s*\{(\S+)\}\s*,\s*(.*)"
        pattern = re.compile(regex)
        
        # lines is one big file string -> m is each match (easier to work with than each line from file is a string, then find the one match per line)
        for m in pattern.finditer(lines):
            row = int(m.group(1))
            col = int(m.group(2))
            weight = int(m.group(3))
            desc = m.group(4).strip()
            
            if desc == "NAN":
                self.grid[row - 1][col - 1] = "NAN"
                continue
            
            if desc == "UNUSED":
                self.grid[row - 1][col - 1] = None
                continue
            
            container = Container(row, col, weight, desc)
            
            # create property for row and col 
            self.grid[row - 1][col - 1] = container
            
            self.containers.append(container)
            if weight > self.max_weight:
                self.max_weight = weight        

    # |Ph - Sh| < Sum(P0,S0) *0.1
    # Grid col 12 by row 8 
    # Port Side ranges from col 0 to 5
    # Starboard Side ranges from col 6 to 11
    def calculate_balance(self):
        portside_weight = 0
        starboardside_weight = 0
        mid = self.C //2 
        count = 0
        countLeft = countRight = 0
        
        if self.loadedCrane is not None:
            return False
        
        for r in range(self.R):
            for c in range(self.C):
                container = self.grid[r][c]
                
                #check if the container is not UNSED and NAN and not NONE
                if isinstance(container, Container):
                    # if this container is in the grid, it already has a valid description
                    count += 1
                    #check if the column is on the port side
                    if c < mid:
                        countLeft += 1
                        portside_weight += container.weight
                    # else the column is on the Starboard side
                    else:
                        countRight += 1
                        starboardside_weight += container.weight
        
        # toatal weight 
        total_weight = portside_weight + starboardside_weight
        
        # check edge case for 1 container 
        if count <= 1 or total_weight == 0:
            return True
        
        #edge case 3 : 1 container on each side
        if count == 2 and countLeft == 1 and countRight == 1: return True
        
        #check the different 
        different = abs(portside_weight - starboardside_weight)
        
        # if balance = 1 then it is balacne else it is not balance. 
        balance = (different <= (total_weight * 0.1)) 
        
        return balance    
       
    #to represent the states of the ship moves using tuple
    # current state of the ship 
    def stateFetch(self):
        status = [] #holds the states
        for k in range(self.R):
            r = [] # the rows

            for a in range(self.C):
                #getting the cel
                place = self.grid[k][a]
                #if empty
                if place is not None:
                    if place == "NAN" :
                        r.append("NAN")
                    else:
                        r.append(place.weight)

                #sles
                else:
                    r.append(None)
            #getting the row list as a element state in the tuple

            status.append(tuple(r))
        #returning the states
        return tuple(status)
    
    
    def statesNext(self):
        # initializing a list for the next possible moves
        movesNext = []

        if self.loadedCrane is not None: #checkin g crane has shipemnt
            #if has shipment then drop it
            movesNext.extend(self.operationDrop())
        else:
            #if no shipemtn then pickup
            movesNext.extend(self.operationPickup())

        return movesNext #returning

    def diagram(self):
        #looping through R
        for k in range(self.R):
            r = [] # the rows

            for a in range(self.C):
                #getting the cel
                place = self.grid[k][a]
                #if empty
                if place is not None:
                    r.append(str(place.weight).zfill(5))

                #sles
                else:
                    r.append("----")
            print(" ".join(r))

    #ship balance check to see which is side is balanced
    def balanceCheck(self):
        #midpoint
        middle = self.C//2
        rSide = 0 #right side
        #left side
        lSide = 0

        # looping through R
        for k in range(self.R):

            for a in range(self.C):
                # getting the cel
                place = self.grid[k][a]

                if not isinstance(place, Container):
                    continue

                if a >= middle:
                    rSide = rSide + place.weight
                #checking for left side
                else:
                    lSide = lSide + place.weight

        return lSide, rSide


    # manhattent distance crane move cost
    # parameters are the location to go to
    def craneCalcMove(self, rowLoc, columnLoc):
        #current postion of crane
        currentRow = self.cranePosR
        currentCol = self.cranePosC
        
        targetRow = rowLoc
        targetCol = columnLoc
        
        colMin = min(currentCol, targetCol)
        colMax = max(currentCol, targetCol)
        
        #highest row 
        maxHeight = -1
        
        for c in range(colMin, colMax + 1):
            for r in range(self.R-1, -1, -1):
                if self.grid[r][c] is not None:
                    if r > maxHeight:
                        maxHeight = r
                    break
        
        height = maxHeight + 1
        
        upCost = abs(height - currentRow)
        downCost = abs(height - targetRow)
        horizontalCost = abs(targetCol - currentCol)
        
        cost = upCost + downCost + horizontalCost
        return cost


    # helper func 1
    #finding the empty top spot
    def findTopRUnused(self, c):
        #going from bottom to top
        for k in range(self.R):
            place = self.grid[k][c]
            
            # Checking the blocked column
            if place == "NAN":
                return None
            
            # if empty
            if place is None:
                #check the if there is a support below
                if k == 0 or self.grid[k-1][c] is not None:
                    #returning the row if empty
                    return k
        #if column full return none
        return None

    #helper func 2
    #fetching top row
    def topContainerFetch(self,c):
        for k in range(self.R -1, -1, -1):
            place = self.grid[k][c]
            # if not empty empty
            if place and place != "NAN":
                #returning the row if not empty
                return k
        #if empty return none
        return None

    #CRANE OPERATIONS FUNCTIONS
    #drop operation for crane
    def operationDrop(self):
        # initializing a list for the next possible moves
        movesNext = []

        # crane empty end the function
        if self.loadedCrane is None:
            return movesNext

        for c in range(self.C):

            rEmpty = self.findTopRUnused(c)  # getting the top empty

            # checking if top container empty or not
            if rEmpty is None:
                # skipping
                continue
            ValMove = self.craneCalcMove(rEmpty, c)  # calculating the costs of move for the top roe and column
            newState = copy.deepcopy(self)  # deep copy for child state (new one)
            newState.cranePosC = c  # setting the column val
            newState.cranePosR = rEmpty  # setting the row val
            shipment = newState.loadedCrane #container storage

            newState.grid[rEmpty][c] = shipment #keeping the cotainer on the grid
            # making crane empty (container placed)

            newState.loadedCrane = None

            #updating rows and columns
            gridLoc = newState.grid[rEmpty][c]
            #updating col
            gridLoc.column = c +1
            # updating row
            gridLoc.row = rEmpty+1
            moveDetail = f"Move container in [{self.cranePosR + 1:02},{self.cranePosC + 1:02}] to [{rEmpty + 1:02},{c + 1:02}]"
            movesNext.append((newState, ValMove, moveDetail))
        return movesNext  # returning the list of successors


    #pickup logic of crane function

    def operationPickup(self):
        #initializing a list for the next possible moves
        movesNext = []

        #crane not empty end the function
        if self.loadedCrane is not None:
            return movesNext

        for c in range(self.C):

            rTop = self.topContainerFetch(c) #getting the top rowfor the columns

            #checking if top container empty or not
            if rTop is None:
                #skipping
                continue
            ValMove = self.craneCalcMove(rTop, c)  # calculating the costs of move for the top roe and column
            newState = copy.deepcopy(self)  # deep copy for child state (new one)
            newState.cranePosC = c #setting the column val
            newState.cranePosR = rTop #setting the row val
            shipment = newState.grid[rTop][c] #setting the container to load it

            #setting to empty
            newState.grid[rTop][c] = None
            #setting it as container

            newState.loadedCrane = shipment

            if self.cranePosR == self.craneRestR and self.cranePosC == self.craneRestC:
                start_pos_str = "HOME [09,01]"
            else:
                start_pos_str = f"[{self.cranePosR+1:02},{self.cranePosC+1:02}]"

            moveDetail = f"Move from {start_pos_str} to [{rTop+1:02},{c+1:02}]"
            
            movesNext.append((newState,ValMove,moveDetail))
        return movesNext #returning the list of successors

    
    def computeheuristic(self):
        lSide, rSide = self.balanceCheck()
        
        if self.max_weight == 0:
            return 0
        
        total_weight = lSide + rSide
        
        # same as below but consider the loaded crane weight
        if self.loadedCrane is not None:
            h_port = abs((lSide + self.loadedCrane.weight) - rSide) / (2 * self.max_weight)
            h_star = abs(lSide - (rSide + self.loadedCrane.weight)) / (2 * self.max_weight)
            h = min(h_port, h_star)
            total_weight += self.loadedCrane.weight
        else:
            h = abs(lSide - rSide) / (2 * self.max_weight)
        
        # just in case (should never reach heursitic if already balance), but we need this to call it truly admissable
        if total_weight > 0 and abs(lSide - rSide) <= total_weight * 0.1:
            return 0
        
        # intuition - estimating the minimum number of moves requires to balance the ship
        # this is admissable, as h <= the actual cost
        return h

    # Astar search
    def AstarSearch(self):
        
        #initail Node
        # grid, cost, position, parent, move
        # position (r, c)
        node = Node(self, 0, (self.cranePosR ,self.cranePosC), None, "Start")
        node.heuristic = self.computeheuristic()
        
        #prioritize Queue 
        frontier = []
        heapq.heappush(frontier, node)
        
        # list of node that already visited
        explored = set()
        explored.add(self.stateFetch())
        
        # loop to search each node
        while frontier:
            
            # set the current node to the lowest cost f 
            currentNode = heapq.heappop(frontier)
            currentShip = currentNode.ship
            
            #check if the ship is already balance
            if currentShip.calculate_balance():              
                finalShip = copy.deepcopy(currentShip)
                return_cost = (currentShip.craneRestR - currentShip.cranePosR) + (currentShip.cranePosC - currentShip.craneRestC)
                final_cost = currentNode.cost + return_cost
                
                finalShip.cranePosR = finalShip.craneRestR
                finalShip.cranePosC = finalShip.craneRestC
                
                move_str = f"Move from [{currentShip.cranePosR +1 :02},{currentShip.cranePosC +1:02}] to HOME [09,01]"
                
                return Node(finalShip, final_cost, (finalShip.craneRestR, finalShip.craneRestC), currentNode, move_str)
            
            #else continue 
            # go to lower /child branch 
            for childShip, cost, desc in currentShip.statesNext():
                #set the current state to the child state
                childState = childShip.stateFetch()
                
                #check if the state is already visit, then skip
                if childState in explored:
                    continue
                
                # else add to the explored
                explored.add(childState)
                
                currentCost = currentNode.cost + cost
                #create a Node for the current child
                childNode = Node(childShip, currentCost, (childShip.cranePosR, childShip.cranePosC), currentNode, desc)
                childNode.heuristic = childShip.computeheuristic()
                
                # update the frontier
                heapq.heappush(frontier, childNode)
                
        return None
