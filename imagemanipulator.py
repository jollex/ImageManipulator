#!/usr/bin/env python

import sys, os, random, io
from PIL import Image

class ImageManipulator(object):
    def __init__(self, image_path):
        self.image = Image.open(image_path)

    def flip_sections(self, n_rows, n_cols):
        boxes, new_w, new_h = self.get_boxes_and_new_size(n_rows, n_cols)
        for box in boxes:
            region = self.image.crop(box)
            region = region.transpose(Image.ROTATE_180)
            self.image.paste(region, box)

        self.image = self.image.crop((0, 0, new_w, new_h))

    def randomize_sections(self, n_rows, n_cols, ext):
        boxes, new_w, new_h = self.get_boxes_and_new_size(n_rows, n_cols)
        random.shuffle(boxes)

        pairs = []
        for i in range(0, len(boxes), 2):
            pairs.append((boxes[i], boxes[i + 1]))

        for pair in pairs:
            first_box, second_box = pair

            first_region_bytes = io.BytesIO()
            self.image.crop(first_box).save(first_region_bytes, format=ext)
            first_region = Image.open(first_region_bytes)

            second_region_bytes = io.BytesIO()
            self.image.crop(second_box).save(second_region_bytes, format=ext)
            second_region = Image.open(second_region_bytes)

            self.image.paste(first_region, second_box)
            self.image.paste(second_region, first_box)

        self.image = self.image.crop((0, 0, new_w, new_h))

    def get_boxes_and_new_size(self, n_rows, n_cols):
        w, h = self.image.size
        section_width = w / n_cols
        section_height = h / n_rows

        boxes = []
        for i in range(n_rows):
            for j in range(n_cols):
                box = (j * section_width, i * section_height,
                      (j + 1) * section_width, (i + 1) * section_height)
                boxes.append(box)

        return boxes, section_width * n_cols, section_height * n_rows

    def save(self, save_path):
        self.image.save(save_path)

if __name__=='__main__':
    if len(sys.argv) == 5:
        f, e = os.path.splitext(sys.argv[1])
        x, y = int(sys.argv[2]), int(sys.argv[3])
        iterations = int(sys.argv[4])
        for i in range(iterations):
            im = ImageManipulator(f + e)
            im.flip_sections(x, y)
            im.randomize_sections(x, y, e[1:])
            im.save("{}-{}x{}{}".format(f, x, y, e))
            x *= 2
            y *= 2
    else:
        print "Usage: {} <image_path> <n_rows> <n_cols> <iterations>".format(sys.argv[0])
