from cmu_graphics import *
import os, pathlib


# taken from sound demo in @2147 piazza post
# https://piazza.com/class/lkq6ivek5cg1bc/post/2147
def loadSound(relativePath):
    # Convert to absolute path (because pathlib.Path only takes absolute paths)
    absolutePath = os.path.abspath(relativePath)
    # Get local file URL
    url = pathlib.Path(absolutePath).as_uri()
    # Load Sound file from local URL
    return Sound(url)