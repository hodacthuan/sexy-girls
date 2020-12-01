from os import listdir
from os.path import isfile, join
from .constants import *
import sys
from PIL import Image, ImageColor


def joinImages(imgPathList, newImgPath):

    images = [Image.open(x) for x in imgPathList]

    newImg = Image.new('RGB', (1900, 1080),
                       ImageColor.getrgb("#cccccc"))

    xOffset = 0

    for im in images:
        newImg.paste(im, (xOffset, 0))
        xOffset += im.size[0] + 30

    newImg.save(newImgPath)


def getFileList(path):
    return [join(path, f) for f in listdir(path) if isfile(join(path, f))]


def getImageSize(path):
    imgOpened = Image.open(path)
    return imgOpened.size


def getImageListSize(path):
    fileList = getFileList(path)

    result = []
    for imgPath in fileList:
        imgOpened = Image.open(imgPath)
        imgObj = {}
        imgObj['path'] = imgPath
        imgObj['width'] = imgOpened.size[0]
        imgObj['height'] = imgOpened.size[1]

        result.append(imgObj)

    return result
