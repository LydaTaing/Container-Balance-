class Node:
    def __init__(self, ship, cost, position, parent, move):
        self.ship = ship            #
        self.cost = cost            # the actual cost to get to goal - g(n)
        self.heuristic = 0          # The heristic cost to get to goal - h(n)
        self.position = position    # crane position
        self.parent = parent 
        self.move = move            # move cooridination 
    
    # f = g + h 
    # compare the value of f from one node to the other node. 
    def __lt__(self, other):
        return (self.cost + self.heuristic) < (other.cost + other.heuristic)
    
    def equals(self, other):
        return self.ship == other.ship and self.position == other.position
    