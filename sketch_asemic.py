import vsketch
import random as rand
import math
import numpy as np
from dataclasses import dataclass, replace
from typing import List

pageLen = 270                       #the height of our writing block in mm
lineLen = 210                       #the maximum length of a line of text
aphabetLen = 30                     #the number of characters in the language's alphabet
vDiv = 6                            #number of verticle divisions there are on a character
dotProb = 0.3                       #chance of an accent being added in any given spot
accLen = 0.8                        #how long horizontal strokes are
charH = 5.5                           #maximum height of characters
charSizeNoise = 1.2                #how much the size of letters can vary, 1 is no variation, n >= 1
charSizeLineNoise = 1.4             #how much does the character size along an entire line vary (affects all characters on a line)
wordStdv = 10                       #standard deviation of word length
newLineChance = 0.01                #chance that the end of a word also triggers a new line
drawAlphabet = False                #determines if the alphabet of characters is drawn at the top
wiggleMin, wiggleMax = -0.3, 0.4    #maximum verticle offset of one char from the next
lineMin, lineMax = -5, 3            #maximum horizontal offset from one line to the next
lineSpacing = 1.1                  #verticle spacing between lines. 1 is no spacing
spaceLen = 1.5                        #how long spaces between words are
cairnLen = -0.5                     #how long spaces between characters are
charTilt = 0.2                      #how much each char's verticle lines tilt as a ratio to their height
charTiltNoise = 0.2                 #how much the tilt on a character's slashes varies
seedLen = 50                        #how many numbers are generated to determine the shape of a char in the alphabet, just make sure this is big enough that no error occures
maxShrink = 0.3                     #how much smaller letters get at maximum over the height of the page
scribbleSize = 1                    #how much larger than the characters are the scribbles that overlay them
scribbleEnd = 0.7                   #chance of a scribble ending at the end of a word
featureChance = 0.03                #chance of starting a feature
scribbleChance = 1                  #given that a feature will be drawn, what is the chance that the feature is a scribble



#used to generate consistent but random values for character generation. A charSeed will always generate the same char
@dataclass
class CharSeed:
    vals: List[int]
    idx: int

    #returns the next value in the seed
    def query(self) -> int:
        self.idx += 1
        if self.idx >= len(self.vals):
            print("ERROR: querried more than the number of unique vals, looping back...")
            self.idx = 0
        return self.vals[self.idx]
    
    #makes a index-0 copy of this seed
    def Copy(self) -> 'CharSeed':
        return replace(self, idx=0)




class AsemicSketch(vsketch.SketchClass):


    def drawUnderline(self,  vsk: vsketch.Vsketch, p1x, p1y, p2x, p2y, iterations, dy):
        for i in range(iterations):
            vsk.line(p1x, p1y+dy*i, p2x, p2y+dy*i)


    
    def drawScribble(self,  vsk: vsketch.Vsketch, p1x, p1y, p2x, p2y, h, step, noise, iterations):
        for i in range(iterations):
            top = True
            x = p1x
            y = p1y-h
            slope = (p2y - p1y)/(p2x-p1x)
            path = []

            while x <= p2x:
                path.append((x+rand.uniform(-1*noise, noise), y+rand.uniform(-1*noise, noise)))

                x += step
                if top:
                    y += h
                else:
                    y -= h
                top = not top
                y += slope*step
                        
            vsk.polygon(path)


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
        vsk.line(x+h*t*pos, y-h*pos, x+h*t*pos+l, y-h*pos)



    def drawChar(self, vsk: vsketch.Vsketch, charSeed, xPos, yPos, yProg, thisCharH):
        w = 1                                                                   #width of the character in # of verticle slashes
        #thisCharH = charH*rand.uniform(1/charSizeNoise, 1*charSizeNoise)*(1-yProg*maxShrink)        
        thisCharTilt = charTilt + rand.uniform(-charTiltNoise, charTiltNoise)   #the tilt that this char is at
        maxh = math.ceil(vDiv/2) + int(charSeed.query()*math.floor(vDiv/2+1))   #the actual height of this char as a percentage of thisCharH
        
        self.slash(vsk, xPos, yPos, thisCharH, 0, maxh/vDiv, thisCharTilt)      #draws the base slash that all chars have
        
        if charSeed.query() < 0.5:  #conditionally adds a second slash
            w = 2
            accentS = int(charSeed.query()*(maxh-1))  #should be equivalent to above line
            accentE = math.ceil(vDiv/2) + int(charSeed.query()*math.floor(vDiv/2+1))  #should be equivalent to above line
            self.slash(vsk, xPos+accLen, yPos, thisCharH, accentS/vDiv, accentE/vDiv, thisCharTilt)
            for p in range(maxh+1):
                if charSeed.query() < dotProb:
                    self.accentLine(vsk, xPos-accLen, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)
            for p in range(0, accentS):
                if charSeed.query() < dotProb:
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)
            for p in range(accentS, accentE+1):
                if charSeed.query() < dotProb:
                    self.accentLine(vsk, xPos+accLen, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)
                    w = 3

            for p in range(accentE+1, maxh+1):
                if charSeed.query() < dotProb:
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)

            for p in range(maxh+1, accentE+1):
                if charSeed.query() < dotProb:
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)
            
        else:
            for p in range(maxh+1):
                if charSeed.query() < dotProb:
                    self.accentLine(vsk, xPos, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)
                    w = 2
                if charSeed.query() < dotProb:
                    self.accentLine(vsk, xPos-accLen, yPos, accLen, thisCharH, p/vDiv, thisCharTilt)
                    w = 2

        return w*accLen





    
    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("letter", landscape=False)
        vsk.scale("mm")

        #sets the IDs for each of the chars on the page
        charSeedSet = []
        for i in range(aphabetLen):
            seedVals = [rand.random() for _ in range(seedLen)]
            charSeedSet.append(CharSeed(vals=seedVals, idx = 0))

        charList = []  #pregenerates all characters that will be written (with some extra padding)
        wordLen = int(abs(np.random.normal(0, wordStdv))) + 1  #rolling value that determines how long the next word will be
        charCount = 0
        for i in range(lineLen*int(pageLen/(charH*(1-maxShrink)))):
            if charCount < wordLen:  #adds character
                charList.append(rand.choice(charSeedSet).Copy())
                charCount += 1
            else:  #end of word, sets up for new word
                if rand.random() < newLineChance:
                    charList.append(-2)
                else:
                    charList.append(-1)
                charCount = 0
                wordLen = int(abs(np.random.normal(0, wordStdv))) + 1

        #draws the set of characters at the top of the page
        yPos = 0
        if drawAlphabet:
            for i in range(aphabetLen):
                self.drawChar(vsk, charSeedSet[i].Copy(), i*4, 15, 0)
            yPos = 30
        

        #draws in all characters on the page
        xPos = 0
        prevLinexPos = xPos
        charCount = 0
        prevLineWiggle = [0]*lineLen
        while(yPos < pageLen):  #until bottom of page
            yProg = yPos/pageLen  #how close to the bottom of the page we are
            xPos = prevLinexPos + rand.uniform(lineMin, lineMax)
            xPos = max(0, xPos)
            prevLinexPos = xPos
            newLine = False
            lineWiggle = [-1]*lineLen
            x1Crossed = -1
            y1Crossed = -1
            thisLineCharSizeNoise = rand.uniform(1/charSizeLineNoise, 1*charSizeLineNoise)

            yPos += thisLineCharSizeNoise*charH*lineSpacing*(1-(yProg*maxShrink)/2.2)  #moves down by one line
            # if rand.random() < 0.2:
            #     yPos += rand.uniform(4, 6)

            while xPos < lineLen and not newLine:  #until end of line
                if int(xPos) - 1 == -1:  #if at the start of line determine yoffset independently of previous character
                    yOff = max(prevLineWiggle[math.floor(xPos)], rand.uniform(10*wiggleMin, 10*wiggleMax))
                else:                    #otherwise determine it based on prev char
                    if abs((prevLineWiggle[math.floor(xPos)])-((lineWiggle[int(xPos) - 1]) + rand.uniform(wiggleMin, wiggleMax*(1+yProg)))) > 3:  #if theres a big gap between this line and the above line, raise the current line to meet it faster
                        yOff = max(prevLineWiggle[math.floor(xPos)], (lineWiggle[int(xPos) - 1]) + rand.uniform(wiggleMin*2, wiggleMax*(1+yProg)))  #determine y offset in terms of previous char and the char above
                    else:
                        yOff = max(prevLineWiggle[math.floor(xPos)], (lineWiggle[int(xPos) - 1]) + rand.uniform(wiggleMin, wiggleMax*(1+yProg)))  #determine y offset in terms of previous char and the char above

                if yPos + yOff >= pageLen:  #if hit bottom of page
                    break

                if charList[charCount] == -2:  #starts newline
                    newLine = True
                elif charList[charCount] == -1:  #draws space
                    lineWiggle[math.floor(xPos) : math.floor(xPos + spaceLen)] = [yOff]*(math.floor(xPos + spaceLen)-math.floor(xPos))
                    xPos += spaceLen
                    
                    if x1Crossed != -1 and rand.random() < scribbleEnd:
                        if rand.random() < scribbleChance:
                            self.drawScribble(vsk, x1Crossed, y1Crossed, xPos-spaceLen, yPos+yOff, charH*(1-yProg*maxShrink)*scribbleSize, 0.4, 0.6, 2)
                        else:
                            self.drawUnderline(vsk, x1Crossed, y1Crossed, xPos-spaceLen, yPos+yOff, 3, 0.1)  #deactivated, doesnt look great
                        x1Crossed = -1
                        y1Crossed = -1
                    elif x1Crossed == -1 and rand.random() < featureChance:
                        x1Crossed = xPos
                        y1Crossed = yPos+yOff
                else:  #draws char
                    thisCharH = thisLineCharSizeNoise*charH*rand.uniform(1/charSizeNoise, 1*charSizeNoise)*(1-yProg*maxShrink)  #the maximum theoretical height that this char could be
                    xDiff = self.drawChar(vsk, charList[charCount], xPos, yPos + yOff, yProg, thisCharH)
                    xDiff += cairnLen
                    lineWiggle[math.floor(xPos) : math.floor(xPos + xDiff)] = [yOff]*(math.floor(xPos + xDiff) - math.floor(xPos))
                    xPos += xDiff


                charCount += 1

            
            
            #updates the upper limit of how high this line can go
            for i in range(lineLen):
                if lineWiggle[i] == -1:
                    prevLineWiggle[i] = max(0, prevLineWiggle[i]-charH*lineSpacing*(1-yProg*maxShrink))
                else:
                    prevLineWiggle[i] = lineWiggle[i]

            


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    AsemicSketch.display()
