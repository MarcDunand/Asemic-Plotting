import vsketch
import random as rand
import math
import numpy as np

#tertiary only new addition

vDiv = 4                            #number of verticle divisions there are on a character
dotProb = 0.2                       #chance of an accent being added in any given spot
accLen = 0.6                        #how long horizontal strokes are
charH = 5                           #maximum height of characters
wordStdv = 10                       #standard deviation of word length
drawAlphabet = False                #determines if the alphabet of characters is drawn at the top
wiggleMin, wiggleMax = -1, 0.7      #maximum verticle offset of one char from the next
spaceLen = 0                        #how long spaces between words are




class AsemicSketch(vsketch.SketchClass):
    def slash(self, vsk: vsketch.Vsketch, x, y, h, s, e):
        vsk.line(x+(h/2)*s, y-h*s, x+(h/2)*e, y-h*e)

    def dot(self, vsk: vsketch.Vsketch, x, y, h, pos):
        vsk.point(x+(h/2)*pos, y-h*pos)

    def accentLine(self, vsk: vsketch.Vsketch, x, y, l, h, pos):
        vsk.line(x+(h/2)*pos, y-h*pos, x+(h/2)*pos+l, y-h*pos)


    def drawChar(self, vsk: vsketch.Vsketch, seed, xPos, yPos):
        rand.seed(seed)
        w = 1  #width of the character in # of verticle slashes
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
                    self.accentLine(vsk, xPos-accLen, yPos, accLen, thisCharH, p/vDiv)
            for p in range(0, accentS):
                if rand.random() < dotProb:
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv)
            for p in range(accentS, accentE+1):
                if rand.random() < dotProb:
                    self.accentLine(vsk, xPos+accLen, yPos, accLen, thisCharH, p/vDiv)
                    w = 3

            for p in range(accentE+1, maxh+1):
                if rand.random() < dotProb:
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv)

            for p in range(maxh+1, accentE+1):
                if rand.random() < dotProb:
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv)
            
        else:
            for p in range(maxh+1):
                if rand.random() < dotProb:
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv)
                    w = 2
                if rand.random() < dotProb:
                    self.accentLine(vsk, xPos-accLen, yPos, accLen, thisCharH, p/vDiv)
                    w = 2

        return w*accLen





    
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("letter", landscape=False)
        vsk.scale("mm")

        lineLen = 210
        pageLen = 270

        #sets the IDs for each of the chars on the page
        seedSet = []
        for i in range(30):
            seedSet.append(rand.randrange(0, 1000000))

        charList = []  #pregenerates all characters that will be written (with some extra padding)
        wordLen = int(abs(np.random.normal(0, wordStdv))) + 1  #rolling value that determines how long the next word will be
        charCount = 0
        for i in range(lineLen*int(pageLen/charH)):
            if charCount < wordLen:  #adds character
                charList.append(rand.choice(seedSet))
                charCount += 1
            else:  #end of word, sets up for new word
                charList.append(-1)
                charCount = 0
                wordLen = int(abs(np.random.normal(0, wordStdv))) + 1

        #draws the set of characters at the top of the page
        
        yPos = 0
        if drawAlphabet:
            for i in range(len(seedSet)):
                self.drawChar(vsk, seedSet[i], i*4, 15)
            yPos = 30
        
        #draws in all characters on the page
        charCount = 0
        prevLineWiggle = [0]*lineLen
        while(yPos < pageLen):  #until bottom of page
            xPos = 0
            newLine = False
            lineWiggle = [0]*lineLen
            while xPos < lineLen and not newLine:  #until end of line
                if int(xPos) - 1 == -1:  #if at the start of line determine yoffset independently of previous character
                    yOff = max(prevLineWiggle[int(xPos)], rand.uniform(10*wiggleMin, 10*wiggleMax))
                else:                    #otherwise determine it based on prev char
                    yOff = max(prevLineWiggle[int(xPos)], (lineWiggle[int(xPos) - 1]) + rand.uniform(wiggleMin, wiggleMax))  #determine y offset in terms of previous char and the char above

                if yPos + yOff >= pageLen:  #if hit bottom of page
                    break

                if charList[charCount] >= 0:  #draws char
                    xDiff = self.drawChar(vsk, charList[charCount], xPos, yPos + yOff)
                    lineWiggle[int(xPos) : int(xPos + xDiff)] = [yOff]*(int(xPos + xDiff) - int(xPos))
                    xPos += xDiff
                else:  #draws space
                    lineWiggle[int(xPos) : int(xPos + spaceLen)] = [yOff]*spaceLen
                    xPos += spaceLen

                
                if rand.random() <= 1/(max(lineLen - xPos, 1)):  #ends this line
                    newLine = True

                charCount += 1

            prevLineWiggle[:len(lineWiggle)] = lineWiggle
            yPos += charH*1.2  #moves down by one line


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    AsemicSketch.display()
