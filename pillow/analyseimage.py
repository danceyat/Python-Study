import argparse
from PIL import Image
from PIL import ImageStat

commands = [ "lum" ]

def do_lum(image_file):
    with Image.open(image_file) as im:
        l = im.convert("L")
        stat = ImageStat.Stat(l)
        print("lum: mean=%f, rms=%f" % (stat.mean[0], stat.rms[0]))

def buildArgParser():
    parser = argparse.ArgumentParser(
            description="A command tool to analyse image.")
    parser.add_argument("command", choices=commands, help="what do you want")
    parser.add_argument("image", help="path to image file")
    return parser

if __name__ == "__main__":
    parser = buildArgParser()
    args = parser.parse_args()

    eval("do_%s(\"%s\")" % (args.command, args.image))

