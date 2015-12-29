__author__ = 'vahan'

class Shape:
    # color -- shape's color
    # shape --shape's geometry (square triangle, circle)
    # centers=[] -- array of shape's centers
    # contours=[] -- array of shape's contours


    def __init__(self,color=None,shape=None):
        if color!=None:
            self.color=color
        if shape!=None:
            self.shape=shape
        self.centers=[]
        self.contours=[]

    def setColor(self, color):
        self.color=color

    def getColor(self):
        return self.color

    def setShape(self, shape):
        self.shape=shape

    def getShape(self):
        return self.shape

    def addContours(self,contour):
        self.contours.append(contour)

    def getContours(self):
        return self.contours

    def addCenters(self,center):
        self.centers.append(center)

    def getCenters(self):
        return self.centers

    def reset(self):
        self.color=""
        self.shape=""
        self.centers=[]
        self.contours=[]

##testing the performance

# if __name__ == '__main__':
#     shape1=Shape()
#     shape2=Shape("red","triangle")
#     print shape2.getColor()
#     print shape2.getShape()
#     shape1.setColor("green")
#     shape1.setShape("triangle")
#     print shape1.getColor()
#     print shape1.getShape()
#     shape1.reset()
#     print shape1.getColor()
#     print shape1.getShape()
#     listOfShapes=[shape1, shape2]
#     print listOfShapes[0].getColor()
