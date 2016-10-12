import math, string, os
from PIL import Image

def magnitude(vector):
    # vector is a dict object consisting of values on each axis
    return math.sqrt(sum(val ** 2 for val in vector.values()))


def angle(vector1, vector2):
    # calculate the angle of two vectors
    product = 0
    for key, value in vector1.items():
        if key in vector2:
            product += value * vector2[key]
    return product / (magnitude(vector1) * magnitude(vector2))


"""
WTF??
The dimension of vector is just the index of pixel??
What if image is zoomed, rotated or stretched??
"""
def buildVector(image):
    vec = {}
    count = 0
    for i in image.getdata():
        vec[count] = i
        count += 1
    return vec


def loadTemplets():
    # build directory path
    chars = []
    for i in range(ord('0'), ord('9') + 1):
        chars.append(chr(i))
    for ch in string.ascii_lowercase:
        chars.append(ch)
    vectors = []
    for ch in chars:
        for f in os.listdir('res/iconset/%s/' % ch):
            vectors.append((ch,
                    buildVector(Image.open(
                            'res/iconset/%s/%s' % (ch, f)))))
            # print("add vector for '%s' from %s" % (ch, f))
    return vectors


def crackImage(image):
    pass


def getSlices(image):
    found = False
    start = 0
    slices = []
    for x in range(image.size[0]):
        inLetter = False
        for y in range(image.size[1]):
            p = image.getpixel((x, y))
            if p != 255:
                inLetter = True
                break

        if found == False and inLetter == True:
            found = True
            start = x
        if found == True and inLetter == False:
            found = False
            slices.append((start, x))
    # why not return a rectangle??
    # if heights of two image differs, the angle of two vector must be big
    return slices


def biLevelImage(image):
    newImage = Image.new("P", image.size, 255)
    for y in range(image.size[1]):
        for x in range(image.size[0]):
            p = image.getpixel((x, y))
            # how do we get this value?
            if p == 220 or p == 227:
                newImage.putpixel((x, y), 0)
    return newImage


def guessCode(image, templets):
    biImage = biLevelImage(image)
    results = []
    for slices in getSlices(biImage):
        img = biImage.crop((slices[0], 0, slices[1], biImage.size[1]))
        guess = []
        for tmp in templets:
            guess.append((tmp[0], angle(buildVector(img), tmp[1])))
        """
        count = 0
        print(slices[0], slices[1])
        for r in sorted(guess, key=lambda x: x[1], reverse=True):
            print("   ", r)
            count += 1
            if count == 10:
                break
        """
        results.append(max(guess, key=lambda x: x[1]))
    return results


templets = loadTemplets()

"""
# check 'res/captcha.gif'
print("code for 'res/captcha.gif': ", end="")
print("".join(r[0] for r in guessCode(Image.open("res/captcha.gif"), templets)))
"""

# check all examples
allCodes, matchCodes = 0, 0
for name in os.listdir('res/examples/'):
    ans = os.path.splitext(name)[0]
    guess = guessCode(Image.open("res/examples/%s" % (name)), templets)
    guessStr = "".join(r[0] for r in guess)
    print("guessing code for '%s' got '%s'" % (name, guessStr), end="")
    if ans == guessStr:
        print("Match")
        matchCodes += 1
    else:
        print("Not match")
    allCodes += 1
print("Matched %d in %d" % (matchCodes, allCodes))

"""
for r in guessCode(Image.open("res/examples/e80qy3.gif"), templets):
    print(r)
"""

