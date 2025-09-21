class Point():
    def __init__(self, binaryValue):
        self.binaryValue = binaryValue
        self.x = 0
        self.y = 0
        self.identifier = 0
        self.rawValue = 0
        
        
    def SetIdentifier(self, Identifier):
        self.identifier = Identifier
        

    def SetXY(self,x,y):
        self.x = x
        self.y = y 
        
    def __str__(self):
        return f"{self.x}, {self.y}, {self.binaryValue}, {self.identifier}"
        
    
        