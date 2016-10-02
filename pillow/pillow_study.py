from PIL import Image

def roll(image, delta):
    "Roll an image sideways"

    xsize, ysize = image.size

    delta = delta % xsize
    if delta == 0: return image

    part1 = image.crop((0, 0, delta, ysize))
    part2 = image.crop((delta, 0, xsize, ysize))
    image.paste(part2, (0, 0, xsize - delta, ysize))
    image.paste(part1, (xsize - delta, 0, xsize, ysize))

    return image


def split_merge(image):
    r, g, b = im.split()
    im = Image.merge("RGB", (b, g, r))

    return im


"""
geometrical transforms

out = im.resize((128, 128))
out = im.rotate(45) # degrees counter-clockwise

out = im.transpose(Image.FLIP_LEFT_RIGHT)
out = im.transpose(Image.ROTATE_90)
"""

"""
Refer to 'pil-handbook.pdf' for details.
"""