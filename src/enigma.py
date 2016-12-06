class Reflector:
    def __init__(self, name, order):
        self.name = name
        self.order = order

    def substitute(self, char):
        return self.order[ord(char) - 65]


class Rotor(Reflector):
    alpha = 'ABCDEFGHIJKLMNOPQRSTUVWXYZ'

    @classmethod
    def I(rotor):
        return rotor('I',   'EKMFLGDQVZNTOWYHXUSPAIBRCJ', 'Q')

    @classmethod
    def II(rotor):
        return rotor('II',  'AJDKSIRUXBLHWTMCQGZNPYFVOE', 'E')

    @classmethod
    def III(rotor):
        return rotor('III', 'BDFHJLCPRTXVZNYEIWGAKMUSQO', 'V')

    @classmethod
    def IV(rotor):
        return rotor('IV',  'ESOVPZJAYQUIRHXLNFTGKDCMWB', 'J')

    @classmethod
    def V(rotor):
        return rotor('V',   'VZBRGITYUPSDNHLXAWMJQOFECK', 'Z')

    def __init__(self, name, order, notch):
        Reflector.__init__(self, name, order)
        self.ring = 'A'
        self.shift = 'A'
        self.notch = notch

    def set_ring(self, char):
        ringDiff = (ord(char) - 65) - (ord(self.ring) - 65)
        self.ring = char
        n = len(self.order)
        newOrder = self.order[(-ringDiff % n):] + self.order[:(-ringDiff % n)]
        self.order = ""
        for i in range(len(newOrder)):
            self.order += chr((((ord(newOrder[i]) - 65) + ringDiff) % 26) + 65)

    def set_shift(self, char):
        self.shift = char

    def substitute(self, char):
        letter = Reflector.substitute(self, chr((((ord(char) - 65) + (ord(self.shift) - 65)) % 26) + 65))
        return chr(((Rotor.alpha.index(letter) - (ord(self.shift) - 65)) % 26) + 65)

    def inverse(self, char):
        letter = chr(((Rotor.alpha.index(char) + (ord(self.shift) - 65)) % 26) + 65)
        return chr(((self.order.index(letter) - (ord(self.shift) - 65)) % 26) + 65)

    def rotate(self):
        self.shift = chr(65 + (((ord(self.shift) - 65) + 1) % 26))

    def step(self):
        return self.notch == self.shift


class PlugBoard:
    def __init__(self, mapping):
        self.pairDict = {}
        if mapping != '':
            self.set_plugboard(mapping)

    def set_plugboard(self, mapping):
        pairs = mapping.split()
        for pair in pairs:
            self.pairDict[pair[0]] = pair[1]
            self.pairDict[pair[1]] = pair[0]

    def substitute(self, char):
        return self.pairDict.get(char, char)


class Enigma:
    def __init__(self, walzenlage=None, ringstellung=None, steckerverbindungen=None, indicator=None):
        self.rotors = []
        self.reflector = Reflector('B', 'YRUHQSLDPXNGOKMIEBFZCWVJAT')

        if walzenlage is not None:
            self.rotors.append(walzenlage[0])
            self.rotors.append(walzenlage[1])
            self.rotors.append(walzenlage[2])
        else:
            self.rotors.append(Rotor.I())
            self.rotors.append(Rotor.II())
            self.rotors.append(Rotor.III())

        if ringstellung is not None:
            self.set_ringstellung(ringstellung)

        if steckerverbindungen is not None:
            self.steckerverbindungen = PlugBoard(steckerverbindungen)
        else:
            self.steckerverbindungen = PlugBoard('')

        if indicator is not None:
            self.set_indicator(indicator)

    def set_ringstellung(self, settings):
        self.rotors[0].set_ring(settings[0])
        self.rotors[1].set_ring(settings[1])
        self.rotors[2].set_ring(settings[2])

    def set_stecker(self, steckerverbindungen):
        self.steckerverbindungen = steckerverbindungen

    def set_indicator(self, indicator):
        self.rotors[0].set_shift(indicator[0])
        self.rotors[1].set_shift(indicator[1])
        self.rotors[2].set_shift(indicator[2])

    def advance_rotors(self):
        if self.rotors[1].step():
            self.rotors[1].rotate()
            self.rotors[0].rotate()
        if self.rotors[2].step():
            self.rotors[1].rotate()
        self.rotors[2].rotate()

    def run(self, word):
        plaintext = word.upper()
        cipher = ""

        for char in plaintext:
            letter = char

            self.advance_rotors()

            letter = self.steckerverbindungen.substitute(letter)

            for rotor in reversed(self.rotors):
                letter = rotor.substitute(letter)
            letter = self.reflector.substitute(letter)
            for invRotor in self.rotors:
                letter = invRotor.inverse(letter)

            letter = self.steckerverbindungen.substitute(letter)
            cipher += letter

        return cipher

#Brief Testing
inStr = "ABABCDCDEFEFGHIHIJKJKLMNOPQRQRSSTUTUVWWWWXXYZZZZ"
encEnigma  = Enigma(walzenlage=(Rotor.IV(), Rotor.II(), Rotor.V()), ringstellung="LGY", steckerverbindungen="AJ BU DS FQ GX HN IV LO PR TY", indicator="GNI")
decEnigma  = Enigma(walzenlage=(Rotor.IV(), Rotor.II(), Rotor.V()), ringstellung="LGY", steckerverbindungen="AJ BU DS FQ GX HN IV LO PR TY", indicator="GNI")
ciphertext = encEnigma.run(inStr)
plaintext  = decEnigma.run(ciphertext)

print "Cipher Text: HISSHJXCULMXNOTDHRAGBYPBHUMZJJIXZEUMSPDHOAWPVVBL" # answer
print "Cipher Text:", ciphertext
print "Plain  Text:", plaintext
print "Plain  Text:", inStr
