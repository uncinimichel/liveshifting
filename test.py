from PIL import Image
import io
import pathlib

im = Image.open('./images/italy.png')
im.save('./images/italy2.png')