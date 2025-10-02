import vsketch
import random as rand
import math
import numpy as np



vDiv = 4  #number of verticle divisions there are
dotProb = 0.2 #chance of an accent being added in any given spot
accLen = 0.6 #how long horizontal strokes are
charH = 5 #maximum height of characters
wordStdv = 10 #standard deviation of word length


class AsemicSketch(vsketch.SketchClass):
    def slash(self, vsk: vsketch.Vsketch, x, y, h, s, e):
        vsk.line(x+(h/2)*s, y-h*s, x+(h/2)*e, y-h*e)

    def dot(self, vsk: vsketch.Vsketch, x, y, h, pos):
        vsk.point(x+(h/2)*pos, y-h*pos)

    def accentLine(self, vsk: vsketch.Vsketch, x, y, l, h, pos):
        vsk.line(x+(h/2)*pos, y-h*pos, x+(h/2)*pos+l, y-h*pos)

    def drawChar(self, vsk: vsketch.Vsketch, seed, xPos, yPos):
        rand.seed(seed)
        w = 1
        thisCharH = charH
        maxh = rand.randrange(math.ceil(vDiv/2), vDiv+1)
        self.slash(vsk, xPos, yPos, thisCharH, 0, maxh/vDiv)
        if rand.random() < 0.5:
            w = 2
            accentS = rand.randrange(0, maxh-1)
            accentE = rand.randrange(math.ceil(vDiv/2), vDiv+1)
            self.slash(vsk, xPos+accLen, yPos, thisCharH, accentS/vDiv, accentE/vDiv)
            for p in range(maxh+1):
                if rand.random() < dotProb:
                    #self.dot(vsk, xPos-0.7, yPos, 6, p/4)
                    self.accentLine(vsk, xPos-accLen, yPos, accLen, thisCharH, p/vDiv)
            for p in range(0, accentS):
                if rand.random() < dotProb:
                    #self.dot(vsk, xPos+0.7, yPos, 6, p/4)
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv)
            for p in range(accentS, accentE+1):
                if rand.random() < dotProb:
                    #self.dot(vsk, xPos+0.7*2, yPos, 6, p/4)
                    self.accentLine(vsk, xPos+accLen, yPos, accLen, thisCharH, p/vDiv)
                    w = 3

            for p in range(accentE+1, maxh+1):
                if rand.random() < dotProb:
                    #self.dot(vsk, xPos+0.7, yPos, 6, p/4)
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv)

            for p in range(maxh+1, accentE+1):
                if rand.random() < dotProb:
                    #self.dot(vsk, xPos, yPos, 6, p/4)
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv)
            
        else:
            for p in range(maxh+1):
                if rand.random() < dotProb:
                    #self.dot(vsk, xPos+0.7, yPos, 6, p/4)
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv)
                    w = 2
                if rand.random() < dotProb:
                    #self.dot(vsk, xPos-0.7, yPos, 6, p/4)
                    self.accentLine(vsk, xPos-accLen, yPos, accLen, thisCharH, p/vDiv)
                    w = 2

        xPos += w*accLen

        return xPos






    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("letter", landscape=False)
        vsk.scale("mm")

        lines = 35
        lineLen = 110

        seedSet = []
        for i in range(10):
            seedSet.append(rand.randrange(0, 1000000))

        charList = []
        wordLen = int(abs(np.random.normal(0, wordStdv))) + 1
        charCount = 0
        for i in range(lines*lineLen):
            if charCount < wordLen:
                charList.append(rand.choice(seedSet))
                charCount += 1
            else:
                charList.append(-1)
                charCount = 0
                wordLen = int(abs(np.random.normal(0, wordStdv))) + 1

        
        for i in range(len(seedSet)):
            self.drawChar(vsk, seedSet[i], i*5, 10)

        
        for i in range(lines):
            yPos = i*charH*1.3 + 20
            xPos = 0
            charCount = 0
            wordLen = int(abs(np.random.normal(0, wordStdv))) + 1
            for j in range(lineLen):
                if charList[i*lineLen+j] >= 0:
                    xPos = self.drawChar(vsk, charList[i*lineLen+j], xPos, yPos)
                else:
                    xPos += 2


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    AsemicSketch.display()
