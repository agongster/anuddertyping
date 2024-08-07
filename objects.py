from cmu_graphics import *
from PIL import Image
import random
from wordGen import WordFrequency

# word frequency txt file referenced from https://number27.org/assets/misc/words.txt
# by Jonathan Harris: https://jjh.org/ in https://number27.org/assets/
wordFreq = WordFrequency('words.txt')

class WordList:

    def __init__(self, wordList, listLength):
        self.wordList = wordList
        self.wordSet = set(self.wordList)
        self.listOfWords = self.intoWords()
        self.onScreen = set()
        self.listLength = listLength
        self.wordToIndex = {}
        self.genRandomList()
        self.difficultySort()
    
    def __repr__(self):
        string = ''
        for word in self.listOfWords:
            string += f'{word.word}: {word.difficulty}, '
        return string
    
    def intoWords(self):
        finalList = []
        for word in self.wordList:
            finalList.append(Word(word, False))
        return finalList
    
    def putOnScreen(self, word):
        self.onScreen.add(word)

    def offScreen(self, word):
        onScreenList = list(self.onScreen)
        for screenWord in onScreenList:
            if word == screenWord.word:
                self.onScreen.remove(screenWord)

    def removeWord(self, word):
        wordInd = self.wordToIndex[Word(word, False)]
        if wordInd < len(self.listOfWords):
            self.listOfWords.pop(wordInd)
        if word in self.wordSet:
             self.wordSet.remove(word)

    def addWord(self, word):
        if word not in self.wordSet:
            i = self.wordToIndex[word]
            self.listOfWords.insert(i, word)
            self.wordSet.add(word)

    def genRandomList(self):
        randWordsSet = wordFreq.genRandomWords(self.listLength)
        for nextWord in randWordsSet:
            # add non-repeating words in list
            if nextWord not in self.wordSet:
                self.wordSet.add(nextWord)
                self.wordList.append(nextWord)
                self.listOfWords.append(Word(nextWord, False))

    # sort by difficulty
    def difficultySort(self):
        self.listOfWords = sorted(self.listOfWords, 
        key=lambda word:word.difficulty)
        for i in range(len(self.listOfWords)):
            word = self.listOfWords[i]
            self.wordToIndex[word] = i

    # get sublist depending on game level
    # corresponding difficulty + player's missed words
    def getLevelList(self, currLevel, totalLevels, missedWords):
        length = len(self.listOfWords)
        listSize = length // totalLevels
        indLow = (currLevel-1) * listSize
        indHi = indLow + listSize
        if currLevel >= totalLevels:
            indLow = length - listSize
            indHi = length
        return self.listOfWords[indLow:indHi]

class Word:

    def __init__(self, word, onScreen):
        self.word = word
        self.onScreen = onScreen
        self.frequency = wordFreq.getScaledFreq(word, 10)
        self.hit = 0
        self.difficulty = self.getDifficulty()
        self.incorrect = self.hit

    def __repr__(self):
        return self.word
    
    def __eq__(self, other):
        return type(other) == Word and self.word == other.word

    def __hash__(self):
        return hash(self.word)

    def getDifficulty(self):
        length = len(self.word)
        # length + frequency between 0 and 10
        # 0 is highest frequency (lower difficulty), 10 lowest frequency
        freqScore = self.frequency
        return length + freqScore

class Cow:

    # images by April Gong
    healthyCow = "healthyCow.png"
    sickCow = "sickCow.png"
    deadCow = "deadCow.png"

    def __init__(self, x, y):
        self.healthy = True
        self.image = Cow.makeCMUImage(Cow.healthyCow)
        self.x = x
        self.y = y
        self.deadTimer = 0
        self.dead = False
        self.moveTimer = random.randint(7, 10)
        self.timer = 0
        self.tx = x
        self.ty = y
    
    def poison(self):
        self.healthy = False
        self.image = Cow.makeCMUImage(Cow.sickCow)
    
    def kill(self):
        self.image = Cow.makeCMUImage(Cow.deadCow)
        self.dead = True

    def randCowMove(self, stepsPerSec, xLowLim, xHiLim, yLowLim, yHiLim):
        stepsInSeconds = self.moveTimer * stepsPerSec
        if self.timer >= stepsInSeconds:
            self.timer = 0
            # generate random cow move
            self.tx = random.randint(xLowLim, xHiLim)
            self.ty = random.randint(yLowLim, yHiLim)
        elif self.timer < stepsInSeconds // 2:
            # move towards target
            stepsLeft = stepsInSeconds // 2 - self.timer
            xDist = (self.x-self.tx) / stepsLeft
            yDist = (self.y-self.ty) / stepsLeft
            self.x -= int(xDist)
            self.y -= int(yDist)
            self.timer += 1
        else:
            self.timer += 1

    def makeCMUImage(name):
        image = Image.open(f"images/{name}")
        return CMUImage(image)


class FallingObject:

    # images by April Gong
    poison = "poison.png"
    hay = "hay.png"
    bomb = "bomb.png"
    wolf = "wolf.png"
    closeBomb = "tintBomb.png"
    closeHay = "tintHay.png"
    closePoison = "tintPoison.png"

    def __init__(self, word, objType, x, y, speed, movement="straight", rightLim=0,
                 leftLim=0):
        self.word = word
        self.destroyCount = 0
        self.type = objType
        self.destroy = False
        self.hitLetters = 0
        self.x = x
        self.y = y
        self.xMove = 0
        self.limit = 0
        self.movement = movement
        if movement != "straight":
            distFromLeft = leftLim - x
            distFromRight = rightLim - x
            self.xMove = random.randint(distFromLeft, distFromRight)
            if self.xMove < 0:
                self.leftLimit = x + self.xMove 
                self.rightLimit = x
            else:
                self.leftLimit = x
                self.rightLimit = x + self.xMove

        self.speed = speed
        self.xSpeed = random.randint(1, 3)
        if objType == "poison":
            self.image = FallingObject.makeCMUImage(FallingObject.poison)
            self.closeImage = FallingObject.makeCMUImage(FallingObject.closePoison)
        elif objType == "hay":
            self.image = FallingObject.makeCMUImage(FallingObject.hay)
            self.closeImage = FallingObject.makeCMUImage(FallingObject.closeHay)
        elif objType == "bomb":
            self.image = FallingObject.makeCMUImage(FallingObject.bomb)
            self.closeImage = FallingObject.makeCMUImage(FallingObject.closeBomb)
        elif objType == "wolf":
            self.image = FallingObject.makeCMUImage(FallingObject.wolf)
            self.closeImage = self.image
        else:
            self.image = None
    
    def __repr__(self):
        return f'word: {self.word}, type: {self.type}'

    def danger(self):
        self.image = self.closeImage

    def makeCMUImage(name):
        image = Image.open(f"images/{name}")
        return CMUImage(image)

class Projectile:

    def __init__(self, initX, initY, targetX, targetY, numSteps):
        self.x = initX
        self.y = initY
        self.numSteps = numSteps
        self.steps = 0
        self.tx = targetX
        self.ty = targetY
        self.reachedTarget = False

    def getNextPos(self):
        if self.steps >= self.numSteps:
            self.reachedTarget = True
        else:
            stepsLeft = self.numSteps - self.steps
            xDist = (self.x-self.tx) / stepsLeft
            yDist = (self.y-self.ty) / stepsLeft
            self.x -= xDist
            self.y -= yDist
            self.steps += 1
