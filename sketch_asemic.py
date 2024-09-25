import vsketch
import random as rand
import math
import numpy as np

aphabetLen = 30                      #the number of characters in the language's alphabet
vDiv = 4                            #number of verticle divisions there are on a character
dotProb = 0.2                       #chance of an accent being added in any given spot
accLen = 0.6                        #how long horizontal strokes are
charH = 5                           #maximum height of characters
wordStdv = 10                       #standard deviation of word length
drawAlphabet = True                 #determines if the alphabet of characters is drawn at the top
wiggleMin, wiggleMax = -0.8, 0.6    #maximum verticle offset of one char from the next
spaceLen = 0                        #how long spaces between words are
charTilt = 0.4                      #how much each char's verticle lines tilt as a ratio to their height
startVar = 5                        #how much does the start of each line vary

class AsemicSketch(vsketch.SketchClass):

    

    #creates a verticle slash for this char.
    #x: x cood of this slash, y: y coord of this slash, h: the theoretical maximum slash height
    #s: start %, what percent up h does this slash start, e: end %, what percent up h does this slash end
    #t: tilt, relative to e-s, how tilted is this slash in the x direction
    def slash(self, vsk: vsketch.Vsketch, x, y, h, s, e, t):
        vsk.line(x+h*s*t, y-h*s, x+h*e*t, y-h*e)


    #creates a tiny horizontal line branching from a verticle slash
    #x: x coord of this accent, y: y coord of this slash, l: the length of this slash
    #h: the theoretical maximum slash height, pos: at what percent of h this accent is placed
    #t: the tilt on this accent line
    def accentLine(self, vsk: vsketch.Vsketch, x, y, l, h, pos, t):
        #vsk.line(x+pos*t, y-h*pos, x+pos*t-l, y-h*pos)
        vsk.line(x+h*t*pos, y-h*pos, x+h*t*pos+l, y-h*pos)



    def drawChar(self, vsk: vsketch.Vsketch, seed, xPos, yPos):
        rand.seed(seed)
        w = 1                                               #width of the character in # of verticle slashes
        thisCharH = charH                                   #the maximum theoretical height the char could be
        thisCharTilt = charTilt                             #the tilt that this char is at
        maxh = rand.randrange(math.ceil(vDiv/2), vDiv+1)    #the actual height of this char as a percentage of thisCharH

        self.slash(vsk, xPos, yPos, thisCharH, 0, maxh/vDiv, thisCharTilt)  #draws the base slash that all chars have
        if rand.random() < 0.5:  #conditionally adds a second slash
            w = 2
            accentS = rand.randrange(0, maxh-1)
            accentE = rand.randrange(math.ceil(vDiv/2), vDiv+1)
            self.slash(vsk, xPos+accLen, yPos, thisCharH, accentS/vDiv, accentE/vDiv, thisCharTilt)
            for p in range(maxh+1):
                if rand.random() < dotProb:
                    self.accentLine(vsk, xPos-accLen, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)
            for p in range(0, accentS):
                if rand.random() < dotProb:
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)
            for p in range(accentS, accentE+1):
                if rand.random() < dotProb:
                    self.accentLine(vsk, xPos+accLen, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)
                    w = 3

            for p in range(accentE+1, maxh+1):
                if rand.random() < dotProb:
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)

            for p in range(maxh+1, accentE+1):
                if rand.random() < dotProb:
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)
            
        else:
            for p in range(maxh+1):
                if rand.random() < dotProb:
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)
                    w = 2
                if rand.random() < dotProb:
                    self.accentLine(vsk, xPos-accLen, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)
                    w = 2

        return w*accLen





    
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("letter", landscape=False)
        vsk.scale("mm")

        lineLen = 210
        pageLen = 270

        #sets the IDs for each of the chars on the page
        seedSet = []
        for i in range(aphabetLen):
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
            xPos = rand.uniform(0, startVar)
            print(xPos)
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
