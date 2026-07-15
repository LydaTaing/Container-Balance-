class Container:
    def __init__(self, row, col, weight, desc):
        #setting up the params
        self.row = int(row)
        self.column = int(col)
        self.desc = desc

        try:
            self.weight = int(weight)
        #if invalid weight
        except:
            self.weight = None


