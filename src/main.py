from collections import deque
import time
from english_fitness_statistics.ngram_score import ngram_score as ns
from enigma import *

Monogram  = ns("english_fitness_statistics/english_monograms.txt")
#Bigram    = ns("english_fitness_statistics/english_bigrams.txt")
#Trigram   = ns("english_fitness_statistics/english_trigrams.txt")
Quadgram  = ns("english_fitness_statistics/english_quadgrams.txt")
#Quintgram = ns("english_fitness_statistics/english_quintgrams.txt")

Rotors    = {1: Rotor.I, 2: Rotor.II, 3: Rotor.III, 4: Rotor.IV, 5: Rotor.V}

class EnigmaBreaker:
    def __init__(self, cipher):
        self.best_score                 = float("-inf")
        self.best_walzenlage            = [1, 2, 3]
        self.best_ringstellung          = "AAA"
        self.best_steckerverbindungen   = ""
        self.best_indicator             = "AAA"
        self.cipher                     = cipher

    def new_enigma(self, walzenlage=None, ringstellung=None, steckerverbindungen=None, indicator=None):
        walz = walzenlage if walzenlage is not None else (Rotors[self.best_walzenlage[0]](), Rotors[self.best_walzenlage[1]](), Rotors[self.best_walzenlage[2]]())
        ring = ringstellung if ringstellung is not None else self.best_ringstellung
        stec = steckerverbindungen if steckerverbindungen is not None else self.best_steckerverbindungen
        indi = indicator if indicator is not None else self.best_indicator
        return Enigma(walzenlage=walz, ringstellung=ring, steckerverbindungen=stec, indicator=indi)

    def break_walzenlage_and_indicator(self):
        optimalIndicators = deque()
        for leftRot in range(1, 6):
            lRot = Rotors[leftRot]()
            choose4 = range(1, 6)[:leftRot-1] + range(1, 6)[leftRot:]
            for i in range(len(choose4)): # This middle loop is different, since we need to access the index within the loop!
                middleRot = choose4[i]
                mRot = Rotors[middleRot]()
                choose3 = choose4[:i] + choose4[i+1:]
                for rightRot in choose3:
                    rRot = Rotors[rightRot]()
                    for leftInd in range(ord("A"), ord("Z") + 1):
                        for middleInd in range(ord("A"), ord("Z") + 1):
                            for rightInd in range(ord("A"), ord("Z") + 1):
                                score = Quadgram.score(self.new_enigma(walzenlage=(lRot, mRot, rRot), indicator=(chr(leftInd) + chr(middleInd) + chr(rightInd))).run(self.cipher))
                                if score > self.best_score:
                                    self.best_score = score
                                    self.best_walzenlage = [leftRot, middleRot, rightRot]
                                    self.best_indicator = chr(leftInd) + chr(middleInd) + chr(rightInd)
                                    optimalIndicators.appendleft(self.best_indicator)
        return optimalIndicators

    def break_ringstellung(self):
        optimalIndicators = self.break_walzenlage_and_indicator()
        for optInd in optimalIndicators:
            midInd = optInd[1]
            rightInd = optInd[2]
            for middleRing in range(ord("A"), ord("Z") + 1):
                for rightRing in range(ord("A"), ord("Z") + 1):
                    ring = "A" + chr(middleRing) + chr(rightRing)
                    indi = self.best_indicator[0] + chr((((ord(midInd) - 65) + (middleRing - 65)) % 26) + 65) + chr((((ord(rightInd) - 65) + (rightRing - 65)) % 26) + 65)
                    score = Quadgram.score(self.new_enigma(ringstellung=ring, indicator=indi).run(self.cipher))
                    if score > self.best_score:
                        self.best_score = score
                        self.best_ringstellung = ring
                        self.best_indicator = indi

# Approximately 11 minutes to decipher this.
cipherText = "NPNKANVHWKPXORCDDTRJRXSJFLCIUAIIBUNQIUQFTHLOZOIMENDNGPCB"
eb = EnigmaBreaker(cipherText)
start = time.clock()
eb.break_ringstellung()
end = time.clock()
ne = eb.new_enigma()
print "Cipher Text: ", cipherText
print "Walzenlage:  ", ne.rotors[0].name,  ne.rotors[1].name,  ne.rotors[2].name
print "Indicator:   ", ne.rotors[0].shift, ne.rotors[1].shift, ne.rotors[2].shift
print "Ringstellung:", ne.rotors[0].ring,  ne.rotors[1].ring,  ne.rotors[2].ring
print "Plain Text:  ", ne.run(cipherText)
print "Score:       ", eb.best_score
print "Time:        ", (end - start)
