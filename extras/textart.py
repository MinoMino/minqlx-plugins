"""Converts links to images pasted in chat to the same image, but represented in
unicode. Basically ASCII art, but with unicode.

It can make clients disconnect on images with certain size and aspect ratio due
to it producing too much text and making it overflow the command buffer.

"""

import threading
import requests
import minqlx
import bisect
import random
import os.path
import io
import re

from statistics import mean
from PIL import ImageFont, ImageEnhance, Image

FONT = "minqlx/data/droidsansmono.ttf"
#FONT = "minqlx/data/arial.ttf"
re_image = re.compile(r"^https?://.+/.+\.(?:jpg|png|bmp|gif)$")

class textart(minqlx.Plugin):
    def __init__(self):
        self.add_hook("chat", self.handle_chat)

    def handle_chat(self, player, msg, channel):
        res = re_image.match(msg.lower().strip())
        if not res:
            return

        channel.reply("Fetching...")
        #self.get_image_and_process(msg.strip())
        threading.Thread(target=self.get_image_and_process, args=(msg.strip(),)).start()

    def get_image_and_process(self, url):
        try:
            res = requests.get(url)
            res.raise_for_status()
            f = io.BytesIO(res.content)
            font_data = self.generate_shading_levels(self.code_points())
            text = self.image_to_unicode(f, font_data, width=78)
            self.print_callback(text)
        except Exception as e:
            minqlx.CHAT_CHANNEL.reply("Failed to create text art: {}".format(e))
            raise

    def print_callback(self, text):
        def text_gen():
            for line in text.split("\n"):
                if line.strip("\n"):
                    yield line
                else:
                    continue
        
        gen = text_gen()

        @minqlx.next_frame
        def go():
            try:
                minqlx.CHAT_CHANNEL.reply(next(gen))
                go()
            except StopIteration:
                return
        
        go()

             
    def generate_shading_levels(self, code_points):
        if not os.path.exists(FONT):
            raise RuntimeError("Couldn't find the font '{}'!".format(FONT))
        font = ImageFont.truetype(os.path.abspath(FONT))
        out = {}
        for i in code_points:
            bitmap = font.getmask(chr(i)).convert("L")
            pixels = []
            for x in range(bitmap.size[0]):
                for y in range(bitmap.size[1]):
                    pixels.append(bitmap.getpixel((x, y)))
            
            if pixels:
                key = round(mean(pixels)) + 25
            else:
                key = 0
            
            if key not in out:
                out[key] = [i]
            else:
                out[key].append(i)

        return out

    def image_to_unicode(self, image, font_data, width=None, height=None):
        img = Image.open(image)
        if width and not height:
            ratio = width/img.size[0]
            img = img.resize((width, round(img.size[1] * ratio * 0.5)), Image.BILINEAR)
        elif not width and height:
            ratio = width/img.size[1]
            img = img.resize((round(img.size[0] * ratio), round(height * 0.5)), Image.BILINEAR)
        else:
            img = img.resize((width, round(height * 0.5)), Image.BILINEAR)
        img = img.convert("L")

        # Enhance!
        #contrast = ImageEnhance.Contrast(img)
        #img = contrast.enhance(0.7)
        #sharpen = ImageEnhance.Sharpness(img)
        #img = sharpen.enhance(1.5)

        # Process data.
        keys = sorted(list(font_data.keys()))

        out = ""
        for y in range(img.size[1]):
            for x in range(img.size[0]):
                lum = img.getpixel((x, y))
                index = bisect.bisect(keys, lum) - 1
                out += chr(random.choice(font_data[keys[index]]))
            out += "\n"

        return out

    def code_points(self):
        cp = []
        cp += [i for i in range(33, 128)]
        cp += [i for i in range(192, 255)]
        # Regular spaces get removed if you have more than one next
        # to each other, but the following character doesn't.
        cp.append(ord(" "))
        for c in "^\"%¯¹æ":
            if ord(c) in cp:
                cp.remove(ord(c))

        for i in range(len(cp)):
            yield cp[i]

