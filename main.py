import csv
import multiset
from multiset import FrozenMultiset as Multiset
import hashlib
from itertools import permutations

# The words in the wordlist file represented as unordered sets (multisets or hypervectors)
words_as_multisets = {}
# Anagram combinations (as multisets) that have already need checked for
checked = {}
# Booleans to signal when each challenge target is found
first_found = False
second_found = False
third_found = False


# Converts a word into a hypervector (could me multiset as well, but a pure vector is more efficient)
def wordToVector(word):
    if len(word) == 1 and word != 'a':
        return "'a' is the only one-character word allowed in English"
    vect = [0]*26 # We assume the 26 letters in the English alphabet as the number of dimensions
    try:
        for c in word:
            charNum = ord(c)
            if charNum < 97 or charNum > 122:
                return "invalid characters in word " + str(word)
            vect[ord(c)-97] += 1
    except Exception as e:
        return 'some error while converting word ' + word + ': ' + str(e)
    # We actually return a bag of elements (along with the vector) that will be handy later
    return [word, Multiset(word), vect, sortChars(word)]

# Just get the current time in seconds since we started
def getTimeSoFar():
    global start_time
    return str(time.time()-start_time)

# Given a valid anagram reprsented as a multiset, this function will test all actual related words and
# their permutations (which should also be valid anagrams) to see if any of those match the targets.
def testAnagramsFromMultiset(ms, anagramToTest):
    global first_found
    global second_found
    global third_found
    if len(ms) == 0:
        all_perms = permutations(anagramToTest)
        for p in all_perms:
            res = " ".join(p)
            md5 = hashlib.md5(res.encode()).hexdigest()
            if not first_found and md5 == 'e4820b45d2277f3844eac66c903e84be':
            # if not first_found and md5 == '5205dcd54f03c23faaed2aa4452ebcdd':
                first_found = True
                print('!!!! Found first secret at ' + getTimeSoFar() + ' seconds: "' + res + '"')
            if not second_found and md5 == '23170acc097c24edb98fc5488ab033fe':
                second_found = True
                print('!!!! Found second secret at ' + getTimeSoFar() + ' seconds: "' + res + '"')
            if not third_found and md5 == '665e5bcb0c20062fe8abaaf4628bb154':
                third_found = True
                print('!!!! Found third secret at ' + getTimeSoFar() + ' seconds: "' + res + '"')
            if first_found and second_found and third_found:
                print('-------------------------------------------------------')
                print('\nAll secrets found. Total time: ' + getTimeSoFar())
                print('-------------------------------------------------------')
                exit(0)
        return

    global words_as_multisets
    words = words_as_multisets[ms[0]]
    for w in words:
        testAnagramsFromMultiset(ms[1:], anagramToTest + [w])


# This functions takes an anagram (as multiset) and a list of words.
# The list of words is already guaranteed to have elements only applicable to the anagram
# The function will execute recursively:
#   1. If there are no more characters left to search it means we already searched all the chars
#      in the original global anagram and hence we already have a candidate anagram (as multiset).
#      Therefore we call the function to check the candidate.
#   2. IF we still have characters left then we need to do another search with the remaining (residual)
#      of the anagram. So we calculate the residual and then all relevant words for that residual, so
#      that we can finally call this function recusevely.
def getAnagrams(anagram, wordList, charsLeft, depth=0, anagramSoFar="", start=0, size=100):
    global checked
    if charsLeft == 0:
        testAnagramsFromMultiset(anagramSoFar.split(), [])
        return

    i = 1
    for w in wordList[start:(start+size)]:
        tmp = (anagramSoFar+' '+w[3]).split()
        tmp.sort()
        index = " ".join(tmp)
        if (index in checked):
            continue
        checked[index] = True
        i += 1
        # if depth == 0:
            # print(str(i)) #, end="")
        anagramResidual = vecSubstract(anagram, w[2])

        global minLen
        minLen = 1000
        def isWithin(mainSet, w):
            global minLen
            if len(w[0]) < minLen:
                minLen = len(w[0])
            return isSubSet(mainSet, w[2])
        # wordListForRest = [ w for w in wordList if isSubSet(anagramResidual, w[2]) ]
        wordListForRest = [ w for w in wordList if isWithin(anagramResidual, w) ]
        # Smallest word in new word list has to at least fit exactly 1 to n times in the chars left
        if True: # charsLeft % minLen == 0:
            getAnagrams(anagramResidual, wordListForRest, charsLeft-len(w[0]), depth+1, anagramSoFar+" "+w[3])

    return


def sortChars(word):
    tmp = [c for c in word]
    tmp.sort()
    return "".join(tmp)

def isSubSet(s1, s2):
    for i in range(26):
        if s1[i] - s2[i] < 0:
            return False
    return True

def vecSubstract(v1, v2):
    return [v1[i]-v2[i] for i in range(26)]
        
import time

start_time = time.time()
print('Start Time: ' + str(start_time))
print('----------------------------------')
with open('wordlist', newline='') as csvfile:
    anagram = 'poultryoutwitsants'
    # anagram = 'atsiwatengshichtysit'
    anagSet = Multiset(anagram)
    anagVector = wordToVector(anagram)[2]
    minLen = len(anagram)

    fileReader = csv.reader(csvfile, delimiter=',')
    words_raw = [row[0].lower() for row in fileReader]
    print('Raw words: ' + str(len(words_raw)))
    words_raw.sort(reverse=False, key=lambda w: len(anagram) - len(w))

    words = [ wordToVector(w) for w in words_raw ]
    words = [ w for w in words if isinstance(w, list) ]
    print('Good words: ' + str(len(words)))

    words_applicable = [ v for v in words if v[1].issubset(anagSet) ]
    print('Applicable words: ' + str(len(words_applicable)))

    # PERFORMANCE: Quick function that will serve as initializer for 'words_as_multisets' as well. Will save an entire iteration over the wordlist
    def notThere(sw, w):
        if sw in words_as_multisets:
            words_as_multisets[sw].append(w)
            return False
        else:
            words_as_multisets[sw] = [w]
            return True
    
    words_applicable_as_multisets = [ w for w in words_applicable if notThere(w[3], w[0])]
    print('Applicable words as hypervectors(multisets): ' + str(len(words_applicable_as_multisets)))
    print('Anagram length: ' + str(len(anagram)))
    print("\n")

    # PERFORMANCE: Do this in batches (better memory management when passing lists recursively, not extrictly necessary but preferable)
    batch_size=100
    num_batches = int(len(words_applicable_as_multisets) / batch_size) + 1
    for start in range(num_batches):
        getAnagrams(anagram=anagVector, wordList=words_applicable_as_multisets, charsLeft=len(anagram), start=start*batch_size,size=batch_size)

    end_time = time.time()
    print('End Time: ' + str(start_time))
    print('-------------------------------------------------------')
    print('\nEntire set traversed. Total time: ' + str(end_time - start_time))
    print('-------------------------------------------------------')

