import vsketch
import random as rand
import math
import numpy as np
from dataclasses import dataclass, replace
from typing import List

aphabetLen = 10                     #the number of characters in the language's alphabet
vDiv = 6                            #number of verticle divisions there are on a character
dotProb = 0.2                       #chance of an accent being added in any given spot
accLen = 0.6                        #how long horizontal strokes are
charH = 4                           #maximum height of characters
charSizeNoise = 1.05                 #how much the size of letters can vary, 1 is no variation, n >= 1
wordStdv = 10                       #standard deviation of word length
newLineChance = 0.025                #chance that the end of a word also triggers a new line
drawAlphabet = False                #determines if the alphabet of characters is drawn at the top
wiggleMin, wiggleMax = -0.3, 0.35    #maximum verticle offset of one char from the next
lineMin, lineMax = -5, 3            #maximum horizontal offset from one line to the next
spaceLen = 1                        #how long spaces between words are
cairnLen = -0.2                        #how long spaces between characters are
charTilt = 0.2                      #how much each char's verticle lines tilt as a ratio to their height
charTiltNoise = 0.03                 #how much the tilt on a character's slashes varies
seedLen = 50                        #how many numbers are generated to determine the shape of a char in the alphabet, just make sure this is big enough that no error occures




#used to generate consistent but random values for character generation. A charSeed will always generate the same char
@dataclass
class CharSeed:
    vals: List[int]
    idx: int

    #returns the next value in the seed
    def query(self) -> int:
        self.idx += 1
        if self.idx >= len(self.vals):
            print("ERROR: querried more than the number of vals, looping back...")
            self.idx = 0
        return self.vals[self.idx]
    
    #makes a index-0 copy of this seed
    def Copy(self) -> 'CharSeed':
        return replace(self, idx=0)




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
        vsk.line(x+h*t*pos, y-h*pos, x+h*t*pos+l, y-h*pos)



    def drawChar(self, vsk: vsketch.Vsketch, charSeed, xPos, yPos):
        w = 1                                                                   #width of the character in # of verticle slashes
        thisCharH = charH*rand.uniform(1/charSizeNoise, 1*charSizeNoise)        #the maximum theoretical height the char could be
        thisCharTilt = charTilt + rand.uniform(-charTiltNoise, charTiltNoise)   #the tilt that this char is at
        #maxh = rand.randrange(math.ceil(vDiv/2), vDiv+1)                       #the actual height of this char as a percentage of thisCharH
        maxh = math.ceil(vDiv/2) + int(charSeed.query()*math.floor(vDiv/2+1))   #should be equivalent to the above line
        
        self.slash(vsk, xPos, yPos, thisCharH, 0, maxh/vDiv, thisCharTilt)      #draws the base slash that all chars have
        
        if charSeed.query() < 0.5:  #conditionally adds a second slash
            w = 2
            #accentS = rand.randrange(0, maxh-1)
            accentS = int(charSeed.query()*(maxh-1))  #should be equivalent to above line
            #accentE = rand.randrange(math.ceil(vDiv/2), vDiv+1)
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

        lineLen = 210
        pageLen = 270

        #sets the IDs for each of the chars on the page
        charSeedSet = []
        for i in range(aphabetLen):
            seedVals = [rand.random() for _ in range(seedLen)]
            charSeedSet.append(CharSeed(vals=seedVals, idx = 0))

        charList = []  #pregenerates all characters that will be written (with some extra padding)
        wordLen = int(abs(np.random.normal(0, wordStdv))) + 1  #rolling value that determines how long the next word will be
        charCount = 0
        for i in range(lineLen*int(pageLen/charH)):
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
                self.drawChar(vsk, charSeedSet[i].Copy(), i*4, 15)
            yPos = 30
        
        #draws in all characters on the page
        xPos = 0
        prevLinexPos = xPos
        charCount = 0
        prevLineWiggle = [0]*lineLen
        while(yPos < pageLen):  #until bottom of page
            xPos = prevLinexPos + rand.uniform(lineMin, lineMax)
            xPos = max(0, xPos)
            prevLinexPos = xPos
            #print(xPos)
            newLine = False
            lineWiggle = [0]*lineLen
            while xPos < lineLen and not newLine:  #until end of line
                if int(xPos) - 1 == -1:  #if at the start of line determine yoffset independently of previous character
                    yOff = max(prevLineWiggle[int(xPos)], rand.uniform(10*wiggleMin, 10*wiggleMax))
                else:                    #otherwise determine it based on prev char
                    yOff = max(prevLineWiggle[int(xPos)], (lineWiggle[int(xPos) - 1]) + rand.uniform(wiggleMin, wiggleMax))  #determine y offset in terms of previous char and the char above

                if yPos + yOff >= pageLen:  #if hit bottom of page
                    break

                if charList[charCount] == -2:  #starts newline
                    newLine = True
                elif charList[charCount] == -1:  #draws space
                    lineWiggle[int(xPos) : int(xPos + spaceLen)] = [yOff]*spaceLen
                    xPos += spaceLen
                else:  #draws char
                    xDiff = self.drawChar(vsk, charList[charCount], xPos, yPos + yOff)
                    lineWiggle[int(xPos) : int(xPos + xDiff)] = [yOff]*(int(xPos + xDiff) - int(xPos))
                    xPos += xDiff + cairnLen


                charCount += 1

            prevLineWiggle[:len(lineWiggle)] = lineWiggle
            yPos += charH*1.2  #moves down by one line


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    AsemicSketch.display()
