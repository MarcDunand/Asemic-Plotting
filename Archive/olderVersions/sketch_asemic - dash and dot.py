import vsketch
import random as rand




class AsemicSketch(vsketch.SketchClass):
    def slash(self, vsk: vsketch.Vsketch, x, y, l, s, e):
        vsk.line(x+(l/2)*s, y-l*s, x+(l/2)*e, y-l*e)

    def dot(self, vsk: vsketch.Vsketch, x, y, l, pos):
        vsk.point(x+(l/2)*pos, y-l*pos)

    def draw(self, vsk: vsketch.Vsketch) -> None:
        vsk.size("letter", landscape=False)
        vsk.scale("mm")

        spacing = 5
        dotProb = 0.2
        
        for i in range(30):
            yPos = i*8 + 20
            xPos = 0
            for j in range(53):
                w = 1
                maxh = rand.randrange(2, 5)
                self.slash(vsk, xPos, yPos, 6, 0, maxh/4)
                if rand.random() < 0.5:
                    w = 2
                    accentS = rand.randrange(0, maxh-1)
                    accentE = rand.randrange(2, 5)
                    self.slash(vsk, xPos+0.7, yPos, 6, accentS/4, accentE/4)
                    for p in range(maxh+1):
                        if rand.random() < dotProb:
                            self.dot(vsk, xPos-0.7, yPos, 6, p/4)
                    for p in range(0, accentS):
                        if rand.random() < dotProb:
                            self.dot(vsk, xPos+0.7, yPos, 6, p/4)

                    for p in range(accentS, accentE+1):
                        if rand.random() < dotProb:
                            self.dot(vsk, xPos+0.7*2, yPos, 6, p/4)
                            w = 3

                    for p in range(accentE+1, maxh+1):
                        if rand.random() < dotProb:
                            self.dot(vsk, xPos+0.7, yPos, 6, p/4)

                    for p in range(maxh+1, accentE+1):
                        if rand.random() < dotProb:
                            self.dot(vsk, xPos, yPos, 6, p/4)
                    
                else:
                    for p in range(maxh+1):
                        if rand.random() < dotProb:
                            self.dot(vsk, xPos+0.7, yPos, 6, p/4)
                            w = 2
                        if rand.random() < dotProb:
                            self.dot(vsk, xPos-0.7, yPos, 6, p/4)
                            w = 3

                xPos += w + 1


    def finalize(self, vsk: vsketch.Vsketch) -> None:
        vsk.vpype("linemerge linesimplify reloop linesort")


if __name__ == "__main__":
    AsemicSketch.display()
