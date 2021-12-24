from cmu_112_graphics import *  # cmu_112_graphics taken from https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html)
from widgets import *
from tkinter import *
from PIL import Image
import random
import time
import math

class CSCup(object):
    def __init__(self,mode, x, y):
        self.mode = mode
        self.x = x
        self.y = y
        self.cupDepth = 32
        self.cupNarrowEndWidth = 17
        self.cupWideEndWidth = 24
        self.toppled = False
        url = "https://encrypted-tbn3.gstatic.com/shopping?q=tbn:ANd9GcQtFK5DJZr_P4iDQCIBPwR9sWzWFkSBqbTaOeTdvkz9S4xsFL0rLwdEE12khu6bHfrWgRKIc9gfNhzEbZOOWD2KNdwCk8t6X9BkSiFwKdpkIac5GGQS192X&usqp=CAc"
        self.spriteStrip = self.mode.loadImage(url)
        self.spriteStrip = self.mode.scaleImage(self.spriteStrip, 1/5)
        self.spriteStrip = self.spriteStrip.transpose(Image.FLIP_TOP_BOTTOM)
        self.spriteStripToppled = \
            self.spriteStrip.transpose(Image.ROTATE_90)

    def getCoordinates(self):
        return (self.x, self.y)

    def move(self, x, y):
        self.x = x
        self.y = y

    def isPointClose(self, x, y):
        return ((self.x-x)**2 + (self.y-y)**2)**0.5<= 20

    def getNarrowEndCoordinates(self):
        return ((self.x - self.cupNarrowEndWidth/2, self.y - self.cupDepth/2,
                 self.x + self.cupNarrowEndWidth/2, self.y - self.cupDepth/2))

    def getWideEndCoordinates(self):
        return ((self.x - self.cupWideEndWidth/2, self.y + self.cupDepth/2,
                 self.x + self.cupWideEndWidth/2, self.y + self.cupDepth/2))

    def topple(self):
        self.toppled = True

    def unTopple(self):
        self.unToppled = True

    def draw(self, canvas):
        if (self.toppled == False):
            canvas.create_image(self.x, self.y,
                            image=ImageTk.PhotoImage(self.spriteStrip))
        else:
            canvas.create_image(self.x, self.y,
                            image=ImageTk.PhotoImage(self.spriteStripToppled))
class CSTable(object):
    def __init__(self, mode, x, y):
        self.mode = mode
        self.x = x
        self.y = y
        url = "https://comps.canstockphoto.com/cartoon-wood-table-eps-vectors_csp49105335.jpg"
        self.spriteStrip = self.mode.loadImage(url)
        self.spriteStrip = self.mode.scaleImage(self.spriteStrip, 5/6)
        self.spriteStrip  = self.spriteStrip.crop((0, 0, 375, 250))

    def draw(self, canvas):
        canvas.create_image(self.x, self.y,
                            image=ImageTk.PhotoImage(self.spriteStrip))

class CSGameMode(Mode):
    def __init__(mode, standalone = False):
        mode.standalone = standalone
        super(CSGameMode, mode).__init__()

    def redrawAll(mode, canvas):
        font = 'Arial 20 bold'
        canvas.create_rectangle(0, 0, mode.width, mode.height, fill = "yellow")
        textStr = f'''
        This is Cup Stacking!
        Stack cups as per the sample image provided in 90 seconds.
        There is a box given inside which you must place your cups.
        There are 3 lines given as reference for the top, middle and
        bottom rows that you must create.
        If you press the Validate buttom, the game will evaluate your
        structure.
        Press any key to start the game'''
        canvas.create_text(mode.width/2, mode.height/2, text=textStr,
                           font = font)

    def keyPressed(mode, event):
        mode.app.setActiveMode(CSGameRealMode(standalone = mode.standalone))

class CSGameRealMode(Mode):
    def __init__(mode, standalone = False):
        mode.standalone = standalone
        super(CSGameRealMode, mode).__init__()

    def appStarted(mode):
        mode.app.miniWon = False
        mode.gameWon = False
        mode.gameOver = False
        mode.switchMode = False
        mode.hideNonCanvasWidgets = False
        mode.maxPlayTime = 90 # seconds

        mode.draggedCup = None
        mode.origX = 0
        mode.origY = 0

        mode.numLevels = 3
        mode.sampleCups = [[[], [], [], []] for i in range(mode.numLevels)]
        mode.stackedCups = [[[], [], [], []] for i in range(mode.numLevels)]
        mode.minCupsPerLevel = 5
        mode.maxCupsPerLevel = 6
        mode.totalCups = mode.maxCupsPerLevel * mode.numLevels
        mode.numLastRowCups = random.randrange(
                mode.minCupsPerLevel, mode.maxCupsPerLevel + 1)

        mode.sampleCups[0][0] = \
            [CSCup(mode,
                   (0.75 *mode.app.width)+(30*i),0.78*(mode.app.height//2))
                   for i in range(mode.numLastRowCups)]
        for cup in mode.sampleCups[0][0]:
            x, y = cup.getCoordinates()
            mode.sampleCups[0][1] += (list(range(int(x)-15,int(x)+15)))

        mode.sampleCups[1][0] = \
            [CSCup(mode,
                   (0.765 *mode.app.width)+(30*i),0.66*(mode.app.height//2))
                   for i in range(mode.numLastRowCups-1)]
        for cup in mode.sampleCups[1][0]:
            i = random.randint(0,1)
            if i == 0:
                mode.sampleCups[1][0].remove(cup)
                if (len(mode.sampleCups[1][0]) <= 3):
                    break
        for cup in mode.sampleCups[1][0]:
            x, y = cup.getCoordinates()
            mode.sampleCups[1][1] += (list(range(int(x)-15,int(x)+15)))

        mode.sampleCups[2][0] = \
            [CSCup(mode,
                   (0.78*mode.app.width)+(30*i),0.54*(mode.app.height//2))
                   for i in range(mode.numLastRowCups - 2)]
        for cup in mode.sampleCups[2][0]:
            i = random.randint(0,1)
            if i == 0:
                mode.sampleCups[2][0].remove(cup)
                if (len(mode.sampleCups[2][0]) <= 2):
                    break
        for cup in mode.sampleCups[2][0]:
            x, y = cup.getCoordinates()
            if x - 13 and x + 13 not in mode.sampleCups[1][0]:
                mode.sampleCups[2][0].remove(cup)
        for cup in mode.sampleCups[2][0]:
            x, y = cup.getCoordinates()
            mode.sampleCups[2][1] += (list(range(int(x)-15,int(x)+15)))

        mode.stackingCups = \
            [CSCup(mode,
                   (40)+(30*i),0.35*(mode.app.height/2))
                   for i in range((mode.totalCups))]

        mode.table = CSTable(mode,300,400)

        placement = (mode.app.width/4, mode.app.height/2,
                     mode.app.width/2, 30)
        if (mode.standalone == False):
            mode.announceWinner = \
                  CaptionBoard(mode.app, placement,
                         "You Won !!!. Press any key to return to main game",
                         fillColor = "orange")
            mode.announceWinner = \
                  CaptionBoard(mode.app, placement,
                         "You Lost. Press any key to return to main game",
                         fillColor = "orange")
        else:
            mode.announceWinner = \
                  CaptionBoard(mode.app, placement,
                         "You Won !!!. Press any key to quit",
                         fillColor = "orange")
            mode.announceLoser = \
                  CaptionBoard(mode.app, placement,
                         "You Lost. Press any key to quit",
                         fillColor = "orange")

        mode.announce = mode.announceLoser

        mode.validateButton = MyButton(mode.app,
                   f'Validate', mode.validateSolution)
        placement = (0.70*mode.app.width, (0.25*mode.app.height) + 250,
                     mode.app.width/8, mode.app.height/20)
        mode.validateButton.placeButton(placement)

        mode.prompts = MyMessage(mode.app, f'Let\'s Play!!!')
        placement = (mode.app.width/4, mode.app.height - 45,
                     mode.app.width/8, mode.app.height/20)
        mode.prompts.placeMessage(placement)

        mode.timerDelay = 100
        mode.clock = MyClock(mode, (30, 300), mode.maxPlayTime)

    def levelWhereCupIsPlaced(mode, cup):
        for i in range(mode.numLevels):
            if (cup in mode.stackedCups[i][0]):
                return i
        return -1
    
    def collateNarrowEndCoords(mode, level):
        sC = mode.stackedCups[level]
        sC[1] = []
        sC[2] = []
        for cup in sC[0]:
            mode.updateNarrowEndCoords(cup, level)
    
    def updateNarrowEndCoords(mode, cup, level):
        sC = mode.stackedCups[level]
        (x0, y0, x1, y1) = cup.getNarrowEndCoordinates()
        x0 = int(x0)
        x1 = int(x1 + 1.0)
        sC[1] += list(range(x0, x1))
        y0 = int(y0)
        y1 = int(y1 - 8.0)
        sC[2] += list(range(y1, y0))

    def sortStackedCupCoords(mode):
        for level in range(mode.numLevels):
            sC = mode.stackedCups[level]
            sC[3] = []
            for cup in sC[0]:
                (x0, y0) = cup.getCoordinates()
                sC[3].append(x0)
            sC[3].sort()
    
    def doesCupRestOnRowBeneath(mode, cup, cupLevel):
        if (cupLevel == 0):
            return True
        sC = mode.stackedCups[cupLevel - 1]
        (xw0, yw0, xw1, yw1) = cup.getWideEndCoordinates()
        xw0 = int(xw0)
        xw1 = int(xw1 + 1.0)
        yw0 = int(yw0)
        yw1 = int(yw1)
        if ((xw0 in sC[1] or xw1 in sC[1]) and \
            (yw0 in sC[2] or yw1 in sC[2])):
            return True
        return False
    
    def doesCupOverlapAnother(mode, cup, cupLevel):
        sC = mode.stackedCups[cupLevel]
        (x0, y0, x1, y1) = cup.getNarrowEndCoordinates()
        x0 = int(x0)
        x1 = int(x1 + 1.0)
        if (x0 in sC[1] or x1 in sC[1]):
            return True
        return False
    
    def mapCupToLevel(mode, cup):
        (x0, y0, x1, y1) = cup.getWideEndCoordinates()
        if 0.87*(mode.app.height//2) < y0 < 0.92*(mode.app.height//2):
            return 0
        if 0.64*(mode.app.height//2) < y0 < 0.80*(mode.app.height//2):
            return 1
        if 0.54*(mode.app.height//2) < y0 < 0.66*(mode.app.height//2):
            return 2
        return -1

    def toppleCup(mode, cup):
        cup.topple()
        cup.move(random.randrange(120, 480), 295)

    def unToppleCup(mode, cup):
        cup.unTopple()

    def mousePressed(mode,event): #https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
        if (mode.gameOver == True):
            return
        for cup in mode.stackingCups:
            if cup.isPointClose(event.x, event.y):
                mode.draggedCup = cup
                (mode.origX, mode.origY) = cup.getCoordinates()
                return
       
    def mouseDragged(mode,event): #https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
        if (mode.gameOver == True):
            return
        if (mode.draggedCup != None):
            mode.draggedCup.move(event.x, event.y)
            return

    def mouseReleased(mode, event):#https://www.cs.cmu.edu/~112/notes/notes-animations-part2.html
        if (mode.gameOver == True):
            return
        if (mode.draggedCup == None):
            return

        cup = mode.draggedCup
        mode.draggedCup = None
        x, y = cup.getCoordinates()
        if (x == mode.origX and y == mode.origY):
            # no movement
            return

        if not 0.15*mode.app.width  < x < 0.55*mode.app.width and \
               0.25*mode.app.height < y < 0.65*mode.app.height:
            cup.move(mode.origX, mode.origY)
            return

        # check if an already placed cup is being moved
        reEvalHigherLevels = False
        level = mode.levelWhereCupIsPlaced(cup)
        print("mapped to existing level: ", level)
        if (level != -1):
            # remove and recompute coordinates
            mode.stackedCups[level][0].remove(cup)
            mode.collateNarrowEndCoords(level)
    
            # since cup was moved we have to check if higher rows
            # properly rest on this row
            reEvalLevel = level
            reEvalHigherLevels = True
    
        # place the cup at the right row
        level = mode.mapCupToLevel(cup)
        if (level == -1):
            print("cannot map to any new level: ", level)
            mode.toppleCup(cup)
        else:
            print("mapped to new level: ", level)
            if (mode.doesCupOverlapAnother(cup, level) == True):
                print("overlap on same row")
                mode.toppleCup(cup)
            elif (mode.doesCupRestOnRowBeneath(cup, level) == True):
                print("rests properly")
                mode.stackedCups[level][0].append(cup)
                mode.updateNarrowEndCoords(cup, level)
            else:
                print("does not rest properly")
                mode.toppleCup(cup)
    
        # if existing cup was moved recheck placements on all higher rows
        while (reEvalHigherLevels == True):
            reEvalHigherLevels = False
            reEvalLevel += 1
            if (reEvalLevel >= mode.numLevels):
                break;
            for tc in mode.stackedCups[reEvalLevel][0]:
                if (mode.doesCupRestOnRowBeneath(tc, reEvalLevel) == True):
                    continue
                print("reeval: does not rest properly")
                mode.stackedCups[reEvalLevel][0].remove(tc)
                mode.toppleCup(tc)
                reEvalHigherLevels = True
            if (reEvalHigherLevels == True):
                mode.collateNarrowEndCoords(reEvalLevel)

    def timerFired(mode):
        if (mode.gameOver == True):
            return
        mode.clock.tick()
        if (mode.clock.remaining() == 0):
            mode.gameOver = True
            mode.prompts.displayMessage(f'Sorry, time\'s up')

    def keyPressed(mode, event):
        if (mode.switchMode == True):
            if (mode.standalone == True):
                quit()
            mode.app.miniWon = mode.gameWon
            mode.app.setActiveMode(mode.app.prevMode)
        if (mode.gameOver == True):
            return

    def validateSolution(mode):
        mode.sortStackedCupCoords()

        for level in range(mode.numLevels):
            if (len(mode.stackedCups[level][0]) !=
                len(mode.sampleCups[level][0])):
                mode.prompts.displayMessage(
                    f'Number of cups in row {level} different from sample arrangement. Try again')
                return

            for i in range(1, len(mode.sampleCups[level][0])):
                (x0, y0) = mode.sampleCups[level][0][i].getCoordinates()
                (x0Prev, y0) = mode.sampleCups[level][0][i-1].getCoordinates()
                j = abs(int(x0 - x0Prev))
                k = abs(int(mode.stackedCups[level][3][i] -
                            mode.stackedCups[level][3][i-1]))
                if k not in range(j-5,j+5):
                    mode.prompts.displayMessage(
                      f'Placement of cups in row {level} does not match sample arrangement. Try again')
                    return

        mode.prompts.displayMessage(f'AWESOME!!!')
        mode.announce = mode.announceWinner
        mode.gameWon = True
        mode.gameOver= True

    def redrawAll(mode, canvas):
        if (mode.gameOver == True):
            mode.hideNonCanvasWidgets = True
        canvas.create_text(0.50*mode.app.width, 0.05*mode.app.height,
                           text = "Cup Stacking!",
                           font="Arial 30 bold")
        canvas.create_text(0.35*mode.app.width, 0.10*mode.app.height,
                           text = "Drag the cups to place them in the box.",
                           font="Arial 15 bold")
        canvas.create_rectangle(0.65*mode.app.width, 0.15*mode.app.height,
                                mode.app.width-10, (0.25*mode.app.height)+200)
        canvas.create_text(0.83*mode.app.width, 0.50*mode.app.height,
                           text = "Structure to be constructed",
                           font="Arial 15 bold")
                        
        canvas.create_rectangle(0.15*mode.app.width, 0.50*(mode.app.height//2),
                                0.55*mode.app.width, 0.45*mode.app.height)
        canvas.create_rectangle(0.15*mode.app.width, 0.90*(mode.app.height//2),
                                0.25*mode.app.width, 0.90*(mode.app.height//2))
        canvas.create_rectangle(0.15*mode.app.width, 0.78*(mode.app.height//2),
                                0.25*mode.app.width, 0.78*(mode.app.height//2))
        canvas.create_rectangle(0.15*mode.app.width, 0.66*(mode.app.height//2),
                                0.25*mode.app.width, 0.66*(mode.app.height//2))
        mode.table.draw(canvas)
        for cup in mode.stackingCups:
            doDraw = True
            for level in range(mode.numLevels):
                if (cup in mode.stackedCups[level][0]):
                    doDraw = False
                    break
            if (doDraw == True):
                cup.draw(canvas)
        for level in range(mode.numLevels -1, -1, -1):
            for cup in mode.sampleCups[level][0]:
                cup.draw(canvas)
        for level in range(mode.numLevels -1, -1, -1):
            for cup in mode.stackedCups[level][0]:
                cup.draw(canvas)
        mode.clock.draw(canvas)
        mode.prompts.drawMessage(canvas, mode.hideNonCanvasWidgets)
        mode.validateButton.drawButton(canvas, mode.hideNonCanvasWidgets)

        if (mode.gameOver == True):
            mode.announce.drawBoard(canvas)
            mode.switchMode = True
        
#these are for running the game standalone.
#uncomment runStandAlone
class CSMiniGame(ModalApp):
    
    def appStarted(app):
        app.margin = 0
        app.getRoot().resizable(0, 0)
        app.setActiveMode(CSGameMode(standalone = True))

def runStandAlone():
    CSMiniGame(width = 900, height = 600)

runStandAlone()
