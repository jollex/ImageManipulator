#!/usr/bin/env python

import sys, os
from PIL import Image

class ImageManipulator(object):
    def __init__(self, image_path, save_path):
        self.save_path = save_path
        self.image = Image.open(image_path)

    def flip_sections(self, n_rows, n_cols):
        w, h = self.image.size

        section_width = w / n_cols
        section_height = h / n_rows

        for i in range(n_rows):
            for j in range(n_cols):
                box = (j * section_width, i * section_height,
                      (j + 1) * section_width, (i + 1) * section_height)
                region = self.image.crop(box)
                region = region.transpose(Image.ROTATE_180)
                self.image.paste(region, box)

        box = (0, 0, section_width * n_cols, section_height * n_rows)
        self.image = self.image.crop(box)

    def save(self):
        self.image.save(self.save_path)

if __name__=='__main__':
    if len(sys.argv) == 4:
        f, e = os.path.splitext(sys.argv[1])
        x, y = int(sys.argv[2]), int(sys.argv[3])
        for i in range(7):
            im = ImageManipulator(f + e, "{}-{}x{}{}".format(f, x, y, e))
            im.flip_sections(x, y)
            im.save()
            x *= 2
            y *= 2
    else:
        print "Usage: {} <image_path> <n_rows> <n_cols>".format(sys.argv[0])
