#!/usr/bin/python

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

def UniqueBigrams():
    Bigrams = {}
    for l in range(ord("A"), ord("Z") + 1):
        c = l - 65
        lchr = chr(l)
        remainingAlphabet = range(ord("A"), ord("Z") + 1)[:c] + range(ord("A"), ord("Z") + 1)[c+1:]
        for r in remainingAlphabet:
            rchr = chr(r)
            if lchr not in Bigrams:
                Bigrams[lchr] = []
            Bigrams[lchr].append(rchr)
    return Bigrams

def Bigrams():
    Bigrams = {}
    for l in range(26):
        lchr = chr(l + 65)
        for r in range(26):
            rchr = chr(r + 65)
            if lchr not in Bigrams:
                Bigrams[lchr] = []
            Bigrams[lchr].append(rchr)
    return Bigrams

class EnigmaBreaker:
    def __init__(self, cipher):
        self.best_score                 = float("-inf")
        self.best_walzenlage            = [1, 2, 3]
        self.best_ringstellung          = "AAA"
        self.best_steckerverbindungen   = ""
        self.best_indicator             = "AAA"
        self.ngram                      = Quadgram
        self.cipher                     = cipher

    def new_enigma(self, walzenlage=None, ringstellung=None, steckerverbindungen=None, indicator=None):
        walz = walzenlage if walzenlage is not None else (Rotors[self.best_walzenlage[0]](), Rotors[self.best_walzenlage[1]](), Rotors[self.best_walzenlage[2]]())
        ring = ringstellung if ringstellung is not None else self.best_ringstellung
        stec = steckerverbindungen if steckerverbindungen is not None else self.best_steckerverbindungen
        indi = indicator if indicator is not None else self.best_indicator
        return Enigma(walzenlage=walz, ringstellung=ring, steckerverbindungen=stec, indicator=indi)

    def break_without_ringstellung_and_plugboard(self):
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
                                score = self.ngram.score(self.new_enigma(walzenlage=(lRot, mRot, rRot), indicator=(chr(leftInd) + chr(middleInd) + chr(rightInd))).run(self.cipher))
                                if score > self.best_score:
                                    self.best_score = score
                                    self.best_walzenlage = [leftRot, middleRot, rightRot]
                                    self.best_indicator = chr(leftInd) + chr(middleInd) + chr(rightInd)
                                    optimalIndicators.appendleft(self.best_indicator)
        return optimalIndicators

    def break_without_plugboard(self):
        optimalIndicators = self.break_without_ringstellung_and_plugboard()
        for optInd in optimalIndicators:
            midInd = optInd[1]
            rightInd = optInd[2]
            for middleRing in range(ord("A"), ord("Z") + 1):
                for rightRing in range(ord("A"), ord("Z") + 1):
                    ring = "A" + chr(middleRing) + chr(rightRing)
                    indi = self.best_indicator[0] + chr((((ord(midInd) - 65) + (middleRing - 65)) % 26) + 65) + chr((((ord(rightInd) - 65) + (rightRing - 65)) % 26) + 65)
                    score = self.ngram.score(self.new_enigma(ringstellung=ring, indicator=indi).run(self.cipher))
                    if score > self.best_score:
                        self.best_score = score
                        self.best_ringstellung = ring
                        self.best_indicator = indi

    def break_full(self):
        self.break_without_plugboard()
        for l in range(26):
            lchr = chr(l + 65)
            s = lchr + ": "
            for r in range(1, 26 - l):
                rchr = chr(r + 65 + l)
                stec = ""
                for p in self.best_steckerverbindungen.split():
                    if lchr not in p and rchr not in p:
                        stec = (stec + " " + p).strip()
                stec = (stec + " " + lchr + rchr).strip()
                score = self.ngram.score(self.new_enigma(steckerverbindungen=stec).run(self.cipher))
                if score > self.best_score:
                    self.best_score = score
                    self.best_steckerverbindungen = stec
                    break

def test():
    # Approximately 11 minutes to decipher this using Python.
    #cipherText = "NPNKANVHWKPXORCDDTRJRXSJFLCIUAIIBUNQIUQFTHLOZOIMENDNGPCB"
    #eb = EnigmaBreaker(cipherText)
    #start = time.clock()
    #eb.break_full()
    #end = time.clock()
    #ne = eb.new_enigma()
    #print "Cipher Text:        ", cipherText
    #print "Walzenlage:         ", ne.rotors[0].name,  ne.rotors[1].name,  ne.rotors[2].name
    #print "Indicator:          ", ne.rotors[0].shift, ne.rotors[1].shift, ne.rotors[2].shift
    #print "Ringstellung:       ", ne.rotors[0].ring,  ne.rotors[1].ring,  ne.rotors[2].ring
    #print "Steckerverbindungen:", eb.best_steckerverbindungen
    #print "Plain Text:         ", ne.run(cipherText)
    #print "Score:              ", eb.best_score
    #print "Time:               ", (end - start)

    # Approximately 15 minutes to decipher this using PyPy instead of Python.
    # Using Python I estimate it would have taken 5 or more hours.
    # Moral of the story: this should have been done in C, not Python.
    longCipherText          = "PVUKORVJDUEQVNTAMIRGNIBLOFVGDTPEVBLCGDLYDDCVQMDGCYPVAQKUWNTPJBUAZQDABYKVDJMSAJDMYBQTKYYIZYEGTEEDUDXWTSKRJUNKJKHUYNGBEQFQJSHJEBTQXYLEPMJWJMXXTDVNFGHNKMIFWXYFBLKFXAMILOHKSENKEFHTIDZQXJINCYYJMCNPCIUVJUSABOLOYUXIHESCGLKMBXELALCMECQRXGWVHKVMOTDOGACKPOQIMDJLMFBVAVUTRCFWVTMTIQCKKHBJEWONWRCEXMLALFMLMONLLPGZAJSITQIJLJXZCIWLXAPFGVWIXGRPNWIFWTREWLKBASINMFFVFSNULPQLFDLRPWJSTENSKPJORSBVPYXWGCWCFBHBNQXDWUAGIQKJMKYBVKXOTXFXTYQIRROQLBLQLROKBWZJOHCGTHCJQFDCVVSKPJVNLEMDMJTTSYNFFHYNEQBXJADJHEFUPKPVXLSNSVSJSYQKJIYRUMGACRGBXIRDBLUQPLLAJNNESLWMQYSWJUJOPHSBUOFWLQKSDKHMSRPEJTETJMSXOKBGKGAITKTPXSFAYRWIDXAWKICZGFOHWKUXNISYQFSWGNCZSZKEKBLGYJFHAITRBNJRTLLJSXIEKZOIHUUHPJNAYPHKDAEYGNIDJNPKDEDJASSQWLUTSIBNYDUFFUWHKOLASVJRNABDEIAHPFWKWBXXPEQMZULSOEHTJPWSWAHWOSWCTFWERXGKHHKVYIEVHEOFHSBOSOYAAMGVKPJLPFPHTHILHOXCSPMDQZJAPPPRBWTPUUXIYJIZSCOWVFGTTMXULPVNJXISRIWJGWICKUIADBXDFNRXVYPGOBCMWLXRQVVIQCBAVYFISLRXXFGLDGZVVMWLEDIYLYUASXXVOBVMNYDFPNQBGZBIJJNOQRJQVYTRONMFNDHPHILAHNBPFURKGNYROKQMSIFHZAKLNULAPIPRUTNMKBFGDBNNQFUXXLYCHDOYZRCDXJXI"
    longPlainText           = "OCTOBERARRIVEDSPREADINGADAMPCHILLOVERTHEGROUNDSANDINTOTHECASTLEMADAMPOMFREYTHENURSEWASKEPTBUSYBYASUDDENSPATEOFCOLDSAMONGTHESTAFFANDSTUDENTSHERPEPPERUPPOTIONWORKEDINSTANTLYTHOUGHITLEFTTHEDRINKERSMOKINGATTHEEARSFORSEVERALHOURSAFTERWARDGINNYWEASLEYWHOHADBEENLOOKINGPALEWASBULLIEDINTOTAKINGSOMEBYPERCYTHESTEAMPOURINGFROMUNDERHERVIVIDHAIRGAVETHEIMPRESSIONTHATHERWHOLEHEADWASONFIRERAINDROPSTHESIZEOFBULLETSTHUNDEREDONTHECASTLEWINDOWSFORDAYSONENDTHELAKEROSETHEFLOWERBEDSTURNEDINTOMUDDYSTREAMSANDHAGRIDSPUMPKINSSWELLEDTOTHESIZEOFGARDENSHEDSOLIVERWOODSENTHUSIASMFORREGULARTRAININGSESSIONSHOWEVERWASNOTDAMPENEDWHICHWASWHYHARRYWASTOBEFOUNDLATEONESTORMYSATURDAYAFTERNOONAFEWDAYSBEFOREHALLOWEENRETURNINGTOGRYFFINDORTOWERDRENCHEDTOTHESKINANDSPLATTEREDWITHMUDEVENASIDEFROMTHERAINANDWINDITHADNTBEENAHAPPYPRACTICESESSIONFREDANDGEORGEWHOHADBEENSPYINGONTHESLYTHERINTEAMHADSEENFORTHEMSELVESTHESPEEDOFTHOSENEWNIMBUSTWOTHOUSANDANDONESTHEYREPORTEDTHATTHESLYTHERINTEAMWASNOMORETHANSEVENGREENISHBLURSSHOOTINGTHROUGHTHEAIRLIKEMISSILES"
    walzenlageUsed          = (Rotor.III(), Rotor.V(), Rotor.I())
    ringstellungUsed        = "WFP"
    steckerverbindungenUsed = "AC EI FW GM"
    indicatorUsed           = "FPM"
    eb = EnigmaBreaker(longCipherText)
    start = time.clock()
    eb.break_full()
    end = time.clock()
    ne = eb.new_enigma()
    print "Cipher Text:        ", longCipherText
    print "Walzenlage:         ", ne.rotors[0].name,  ne.rotors[1].name,  ne.rotors[2].name
    print "Indicator:          ", ne.rotors[0].shift, ne.rotors[1].shift, ne.rotors[2].shift
    print "Ringstellung:       ", ne.rotors[0].ring,  ne.rotors[1].ring,  ne.rotors[2].ring
    print "Steckerverbindungen:", eb.best_steckerverbindungen
    print "Plain Text:         ", ne.run(longCipherText)
    print "Score:              ", eb.best_score
    print "Time:               ", (end - start)

if __name__ == "__main__":
    test()
