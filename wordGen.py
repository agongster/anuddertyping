import random

class WordFrequency:

    def __init__(self, txtFile):
        self.txtFile = txtFile
        self.readFile()
        # word: frequency
        self.wordToFrequency = dict()
        self.fillDict()
        self.allWords = list(self.wordToFrequency.keys())

    def readFile(self):
        with open(self.txtFile, 'r') as f:
            fileString = f.read()
        self.fileList = fileString.splitlines()
    
    def fillDict(self):
        for wordGroup in self.fileList:
            extracted = wordGroup.split(',')
            # remove init ( from first word elem
            word = extracted[0][1:]
            # get rid of ) from last elem
            frequency = int(extracted[2][:-1])
            self.wordToFrequency[word] = frequency
            self.totalWords = frequency + 1

    # returns a set of random words of certain length
    def genRandomWords(self, setLength):
        randomWords = set()
        for i in range(setLength):
            randWord = random.choice(self.allWords)
            randomWords.add(randWord)
        return randomWords
    
    # divide words into groupNum groups, each group with same frequency
    def getScaledFreq(self, word, groupNum):
        # groups 1-10
        if word in self.wordToFrequency:
            # higher frequency = lower difficulty
            frequency = self.wordToFrequency[word]
            wordsPerGroup = self.totalWords // groupNum
            freqRank = (frequency // wordsPerGroup) + 1
        else:
            freqRank = 0
        return freqRank
    