from cmu_graphics import *
from objects import *
import random
from PIL import Image
import sounds
import copy

'''
Anudder Typing Game: April Gong
* all images hand-drawn
'''

# referenced from lecture notes
def makeCMUImage(app, name):
    image = Image.open(f"images/{name}")
    return CMUImage(image)

def onAppStart(app):
    app.start = True
    app.width = 600
    app.height = 800
    app.stepsPerSecond = 30
    # the wait for the first level
    app.firstObjWait = 70
    # level changes every 40 seconds
    app.levelChange = 40
    app.textX = app.width // 2
    app.textY = app.height * 3 // 4
    app.scoreX = app.width // 10
    app.scoreY = app.height // 15
    app.levelX = app.width * 9 // 10
    app.levelY = app.height // 15
    app.dangerous = 200
    app.threshold = app.height * 3 // 4
    app.initObjToSpeed = {"poison": 1,
                      "hay": 2,
                      "bomb": 2}
    # images by April Gong
    app.titlepg = makeCMUImage(app, "title.png")
    app.wolfbg = makeCMUImage(app, "wolfbg.png")
    app.overbg = makeCMUImage(app, "wonbg.png")
    app.instructionsbg = makeCMUImage(app, "instructions.png")
    app.cowbg = makeCMUImage(app, 'cowbg.png')

    '''
    moo sound: https://freesound.org/people/toddtruax/sounds/144820/
    by toddtruax on freesound.org
    '''
    app.moo = sounds.loadSound('sounds/moo.mp3')
    '''
    background music: https://freesound.org/people/yummie/sounds/410574/
    CC4.0 Manuel Graf - https://manuelgraf.com
    Manuel Graf
    M.Sc. Media Informatics
    Munich, Germany
    manuelgraf.com
    mg@apfelkuh.de
    '''
    app.gameMusic = sounds.loadSound('sounds/bgMusic.mp3')
    app.bgMusic = sounds.loadSound('sounds/bgMusic.mp3')
    '''
    battle music: https://freesound.org/people/TheoJT/sounds/510953/
    by TheoJT on fressound.org
    '''
    app.battleMusic = sounds.loadSound('sounds/battlemusic.mp3')
    
    '''
    projectile sound: https://freesound.org/people/jeckkech/sounds/391660/
    by jeckkech on freesound.org
    '''
    app.projectileSound = sounds.loadSound('sounds/projectileSound.wav')
    '''
    explosion sound: https://freesound.org/people/BennettFilmTeacher/sounds/523785/
    by BennettFilmTeacher on freesound.org
    '''
    app.explosion = sounds.loadSound('sounds/explosion.aiff')
    app.bg = app.titlepg

    restart(app)

def restart(app):
    # reset the frequency of new objects appearing
    app.newObjWait = app.firstObjWait
    app.battleMusic.pause()
    app.gameMusic.play(loop=True)

    app.cows = [Cow(generateRandX(), generateRandY(650, 700)), Cow(generateRandX(), 
                                                                   generateRandY(650, 700))]
    app.objects = []
    app.projectiles = []
    app.wordToObject = dict()
    app.objToSpeed = copy.deepcopy(app.initObjToSpeed)
    app.movements = ["straight", "zigzag"]

    app.textColor = 'black'
    app.input = ""
    app.correctTyped = False

    # cow related words
    lst = ["pasture", "shepherd", "bonanza",
           "moooooo", "milk", "udders", "bovine", "cattle", "heifer", "dairy",
           "grazing", "hooves", "calves", "holstein", "angus", "jersey", "hereford",
           "brahman", "charolais", "limousin", "simmental", "highland", "shorthorn",
           "ayrshire", "longhorn", "dexter", "beef", "manure", "barn", "silage", 
           "grazing", "livestock", "muzzle", "bullpen", "meadow", "field",
           "pastoral", "ranch", "agriculture", "milkmaid", "lactation", "ruminant",
           "herefordshire", "stockyard", "bovinophile", "bovinophobia", "milkshake",
           "cheesemaking", "clover", "meadowlark", "mootivation", "moosic", "cowcatcher",
           "cowpox", "cowabunga", "cowpoke"]

    # generate 1000 more random words
    app.wordList = WordList(lst, 1000)
    app.missedWords = set()

    app.projR = 5
    app.projSteps = 15
    app.projX = app.textX
    app.projY = app.textY

    app.counter = 0
    app.score = 0

    app.inGame = False
    # level increases every 30 seconds
    app.level = 1
    app.totalLevels = 10
    app.won = False
    app.gameOver = False
    app.endMessage = 'NO MORE COWS TT'
    app.paused = False
    app.instructions = False
    app.bossLevel = False
    app.wolfLevel = 10
    app.wolfSpeed = 1
    app.wolvesFalling = 0
    app.nextWolfWait = 90

def redrawAll(app):
    # draw background
    drawImage(app.bg, 0, 0)
    if app.start:
        drawLabel("Press space to continue", app.width//4, app.height*7//8, 
        font='monospace', size=16, fill='white')
    if app.instructions:
        drawLabel("Press space to continue", app.width//4, 25, 
                  font='monospace', size=16, fill='black')
    if not app.start and not app.instructions:
        # draw score
        drawLabel(f'Score: {int(app.score)}', app.scoreX, app.scoreY, font='monospace',
                  bold=True, fill=app.textColor)
        drawLabel(f'Level: {app.level}', app.levelX, app.levelY, font='monospace',
                  bold=True, fill=app.textColor)
        # draw cows
        drawCows(app)
        if app.inGame and not app.paused:
            # display user input text
            drawLabel(app.input, app.textX, app.textY, font='monospace', bold=True, 
                      size=16, fill=app.textColor)
            # draw falling objects and projectiles
            drawFalling(app)
            drawProjectiles(app)
        elif not app.gameOver and not app.start:
            # display current level
            drawLabel(f'Level: {app.level}', app.width//2, app.height//2, font='monospace', 
                      bold=True, size=24)
        elif app.gameOver:
            drawLabel(app.endMessage, app.width//2, app.height//2, font='monospace', 
                      bold=True, size=24, fill='white')
            drawLabel(f"Final Score: {app.score}", app.width//2, app.height//2+150,
                      font='monospace', bold=True, size=16, fill='white')
            drawLabel("Press space to restart", app.width//2, app.height//2+100,
                      font='monospace', bold=True, size=16, fill='white')

def drawFalling(app):
    for i in range(len(app.objects)):
        obj = app.objects[i]
        # not boss level, make objects small
        if app.level <= app.wolfLevel:
            imageWidth, imageHeight = 50, 50
        # boss level, make wolves big
        else:
            imageWidth, imageHeight = 200, 200
        textXShift, textYShift = imageWidth//2, imageHeight + 10
        drawImage(obj.image, obj.x, obj.y, width=imageWidth, height=imageHeight)
        # draw the word on the object
        # draw hit words in red
        hitInd = obj.word.hit
        # draw hit letters
        drawLabel(obj.word.word[:hitInd] + " " * (len(obj.word.word)-hitInd), obj.x+textXShift, 
                  obj.y+textYShift, align="center", size=20, fill="red", font='monospace', bold=True)
        # draw unhit letters
        drawLabel(" " * (hitInd+1) + obj.word.word[hitInd:], obj.x+textXShift, obj.y+textYShift, align="center", 
                  font='monospace', bold=True, size=20, fill=app.textColor)

def drawProjectiles(app):
    for proj in app.projectiles:
        drawCircle(proj.x, proj.y-10, app.projR)

def drawCows(app):
    for i in range(len(app.cows)):
        cow = app.cows[i]
        drawImage(cow.image, cow.x, cow.y, width=170, height=85)

def onKeyPress(app, key):
    # pause and unpause the game when 0 is pressed
    if key == '0':
        app.paused = not app.paused
    # skip to level of digit
    elif key.isdigit():
        app.level = int(key)
        levelSettings(app)
    # skip to boss level
    elif key == "tab":
        app.level = app.wolfLevel + 1
        levelSettings(app)
    elif key == "space":
        # move to instructions screen
        if app.start:
            app.bg = app.instructionsbg
            app.start = False
            app.instructions = True
        # move to game screen
        elif app.instructions:
            app.bg = app.cowbg
            app.instructions = False
        # restart the game
        elif app.gameOver:
            app.gameOver = False
            app.bg = app.cowbg
            app.gameMusic = app.bgMusic
            restart(app)
        # in game, add space to input
        elif app.inGame:
            app.input += " "
    elif key == "backspace":
        if app.input != "":
            app.input = app.input[:-1]
    elif key == "enter":
        if Word(app.input, True) in app.wordList.onScreen:
            hitObj = app.wordToObject[app.input]
            objectHit(app, hitObj)
        app.input = ""
    elif len(key) == 1 and key != '0' and app.inGame:
        app.input += key
    # sees if it hits any of the right letters
    for screenWord in app.wordList.onScreen:
        for lastInd in range(len(app.input)+1):
            if app.input[:lastInd] == screenWord.word[:lastInd]:
                screenWord.hit = lastInd
            else:
                if screenWord.hit != 0:
                    screenWord.incorrect = lastInd
                else:
                    break

def onStep(app):
    # change background when game over
    if app.gameOver:
        app.bg = app.overbg
    # game over when no cows
    if len(app.cows) == 0 and not app.gameOver:
        app.score += 3**app.level
        app.inGame = False
        app.gameOver = True
    if not app.start and app.inGame and not app.paused and not app.instructions:
        # every 30 seconds, level increases
        if not app.bossLevel and app.counter != 0 and app.counter % (app.stepsPerSecond * app.levelChange) == 0:
            app.level += 1
            levelSettings(app)
        # generate a new falling object every set amount of time
        elif app.counter == 0 or app.counter % app.newObjWait == 0:
            # generate the boss wolf
            if app.level > app.wolfLevel:
                # cue the battle music !
                app.gameMusic = app.battleMusic
                app.battleMusic.play(loop=True)
                app.newObjWait = app.nextWolfWait
                app.bossLevel = True
                app.textColor = 'white'
                # still missed words left to go
                if len(app.missedWords) != 0:
                    newObj = generateWolf(app)
                    app.objects.append(newObj)
                # no more missed words, game won if no wolves falling
                elif app.wolvesFalling == 0:
                    app.won = True
                    app.endMessage = 'YOUR COWS ARE SAFE FOR THE NIGHT'
                    app.gameOver = True
                    app.inGame = False
                # change the background to indicate boss level
                app.bg = app.wolfbg
            else:
                newObj = generateRandObj(app)
                app.objects.append(newObj)
        app.counter += 1
        # update positions of falling objects
        for obj in app.objects:
            # make move depending on object move type
            if obj.movement == "straight":
                moveStraight(obj)
            elif obj.movement == 'zigzag':
                moveZigzag(obj)
            # indicate position is approaching threshold
            if app.threshold - obj.y <= app.dangerous:
                obj.danger()
            # destroy if position is beyond threshold
            if obj.y >= app.threshold:
                objectPassed(app, obj)
                destroyObject(app, obj)
            # destroy in projSteps when obj hit
            if obj.destroy:
                if obj.destroyCount >= app.projSteps:
                    destroyObject(app, obj)
                else:
                    obj.destroyCount += 1

        # update positions of projectiles
        for i in range(len(app.projectiles)):
            app.projectiles[i].getNextPos()
            if app.projectiles[i].reachedTarget:
                app.projectiles.pop(i)
        # keep dead cows for 2 seconds
        for cow in app.cows:
            if cow.dead:
                cow.deadTimer += 1
                if cow.deadTimer >= app.stepsPerSecond * 2:
                    # remove cow from list
                    app.cows = app.cows[1:]
            else:
                cow.randCowMove(app.stepsPerSecond, max(0, cow.x-100), 
                                min(app.width, cow.x+100), max(650, cow.y-100), 
                                min(750, cow.y+100))
    elif not app.start and not app.gameOver and not app.instructions:
        # level display counter
        if app.counter >= app.stepsPerSecond * 3:
            app.inGame = True
        app.counter += 1

def levelSettings(app):
    # add object words back to list
    for obj in app.objects:
        app.wordList.addWord(obj.word)
    # how many even levels have gone by, each should decrease wait time
    evenLevelsPassed = app.level // 2
    app.newObjWait = app.firstObjWait - (5 * evenLevelsPassed) 
    # increase speed of each object with each odd level passed
    oddLevelsPassed = (app.level // 2) + (app.level % 2) - 1
    for obj in app.objToSpeed:
        app.objToSpeed[obj] = app.initObjToSpeed[obj] + (0.5 * oddLevelsPassed)
    app.counter = 0
    # reset things
    app.objects = []
    app.projectiles = []
    app.wordToObject = dict()
    app.input = ""
    app.inGame = False

def generateWolf(app):
    # wolf will display missed words
    missedWord = app.missedWords.pop()
    # put the word on the screen
    app.wordList.putOnScreen(missedWord)
    randInt = random.randint(0, len(app.movements) - 1)
    randMove = app.movements[randInt]
    wolfObj = FallingObject(missedWord, "wolf", generateRandX(100, app.width-200),
                            0, app.wolfSpeed, movement=randMove, rightLim=app.width-100,
                            leftLim=100)
    app.wordToObject[missedWord.word] = wolfObj
    app.wolvesFalling += 1
    return wolfObj

def generateRandObj(app):
    # generate a random word from level's wordlist
    leveledList = app.wordList.getLevelList(app.level, app.totalLevels, 
                                            list(app.missedWords))
    randInt = random.randint(0, len(leveledList)-1)
    randWord = leveledList[randInt]
    while randWord in app.wordList.onScreen:
        randInt = random.randint(0, len(leveledList)-1)
        randWord = leveledList[randInt]
    # add word to list of words on screen
    app.wordList.putOnScreen(randWord)
    # remove word so it doesn't appear again for now
    app.wordList.removeWord(randWord.word)

    # generate random object with random word, random movetype
    options = ["poison", "poison", "poison", "bomb", "bomb", "hay"]
    randInt = random.randint(0, len(options)-1)
    randType = options[randInt]
    randInt = random.randint(0, len(app.movements)-1)
    randMoveType = app.movements[randInt]
    randObj = FallingObject(randWord, randType, generateRandX(100, app.width-100), 
                            0, app.objToSpeed[options[randInt]], movement=randMoveType,
                            rightLim=app.width-100, leftLim=100)
    # add word: object to dictionary
    app.wordToObject[randWord.word] = randObj
    return randObj

def generateRandX(leftLim = 0, rightLim = app.width):
    return random.randint(leftLim, rightLim)

def generateRandY(topLim = 0, botLim = app.height):
    return random.randint(topLim, botLim)

def objectPassed(app, obj):
    firstCow = app.cows[0]
    # wolf eats the cows
    if obj.type == "wolf":
        # kill all the cows
        for cow in app.cows:
            cow.kill()
        # update endgame message
        app.endMessage = 'YOUR COWS WERE EATEN'
    if obj.type == "poison":
        # make the first healthy cow sick, or kill if already sick
        if firstCow.healthy:
            firstCow.poison()
        else:
            firstCow.kill()
    elif obj.type == "bomb":
        # kill the cow 
        firstCow.kill()
        app.explosion.play(restart=True)
    updateScore(app, False, obj)
    # add to missed words
    app.missedWords.add(obj.word)

def objectHit(app, obj):
    updateScore(app, True, obj)
    if obj.type == 'wolf':
        app.wolvesFalling -= 1
    if obj.type == "hay":
        app.cows.append(Cow(generateRandX(), generateRandY(650, 700)))
        app.moo.play(restart=True)
    # start setting timer to destroy object in set steps
    obj.destroy = True
    # add projectile towards object
    addProjectile(app, obj)

def updateScore(app, wasHit, obj):
    distFromCows = app.threshold - obj.y
    scaledDistFromCows = int(distFromCows * (10 / app.threshold))
    # if wolf is hit, increase score by level * 300
    if wasHit and obj.type == 'wolf':
        app.score += app.level * 300
    # if wolf eats cows, subtract half of the score
    elif not wasHit and obj.type == 'wolf':
        app.score -= abs(app.score // 2)
    # for a hit object: score + level*2 * difficulty of word * 50 + distance from cows * 10
    if wasHit:
        app.score += (app.level * 2) * (obj.word.difficulty * 50 +
                                        scaledDistFromCows * 10)
    # for a passed object: score - level*10 * difficulty of word * 10
    else:
        app.score -= app.level * 10 * obj.word.difficulty * 10

# take object off screen
def destroyObject(app, obj):
    # remove from objects list
    app.objects = removeObject(app, obj)
    hitWord = obj.word
    # add word back to the list
    if hitWord in app.wordList.wordSet:
        app.wordList.addWord(hitWord)
    # remove its word from onscreen list
    app.wordList.offScreen(hitWord)

def removeObject(app, obj):
    objSet = set(app.objects)
    if obj in objSet:
        objSet.remove(obj)
    return list(objSet)

def moveStraight(obj):
    obj.y += obj.speed

def moveZigzag(obj):
    obj.y += obj.speed
    # object moves left
    if obj.xMove < 0:
        # keep moving to left if space left
        if obj.x > obj.leftLimit:
            obj.x -= obj.xSpeed
        # change movement to right when limit surpassed
        else:
            obj.xMove *= -1
    # object moves right
    elif obj.xMove > 0:
        if obj.x < obj.rightLimit:
            obj.x += obj.xSpeed
        else:
            obj.xMove *= -1

# predict where an object will be in steps
def predictObjPos(obj, steps):
    x = obj.x
    y = obj.y + obj.speed * steps
    if obj.xMove == 0:
        return x, y
    stepsAcrossMove = obj.xMove // obj.xSpeed
    # moving left
    if obj.xMove < 0:
        stepsToLimit = (obj.x - obj.leftLimit) // obj.xSpeed
    # moving right
    elif obj.xMove > 0:
        stepsToLimit = (obj.rightLimit - obj.x) / obj.xSpeed
    stepsAfterLimit = steps - stepsToLimit 
    # doesn't change directions
    if stepsAfterLimit <= 0:
        if obj.xMove < 0:
            x = obj.x - obj.xSpeed * steps
        else:
            x = obj.x + obj.xSpeed * steps
    else:
        runs = 0
        if stepsAcrossMove != 0:
            runs = stepsAfterLimit // stepsAcrossMove
        stepsFromLimit = stepsAfterLimit % stepsAcrossMove
        # equivalent to turning around once and going back, same dir
        if (runs % 2 == 1 and obj.xMove < 0) or (runs % 2 == 0 and obj.xMove > 0):
            x = obj.rightLimit - abs(stepsFromLimit) * obj.xSpeed
        else:
            x = obj.leftLimit + abs(stepsFromLimit) * obj.xSpeed
    return x, y

def addProjectile(app, hitObj):
    tx, ty = predictObjPos(hitObj, app.projSteps)
    if app.bossLevel:
        tx += 100
        ty += 210
    else:
        tx += 25
        ty += 60
    app.projectiles.append(Projectile(app.projX, app.projY, tx, ty, app.projSteps))
    app.projectileSound.play(restart=True)

def main():
    runApp()

if __name__ == '__main__':
    main()  
