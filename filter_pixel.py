#-*- coding:utf-8 -*-

import sys
import numpy as np

from PIL import Image
from collections import Counter


def filter_pixels(path):
    f = Image.open(path)
    f2 = f.convert('L')
    im_array = np.array(f2)
    total_white_pixel = 0
    cnt = Counter()
    for x_arr in im_array:
        for i, pixel in enumerate(x_arr):
                cnt[pixel] += 1

    watermark = 0
    background = int(cnt.most_common(1)[0][0])

    clen = len(cnt)
    elements = cnt.most_common(clen - 1)

    for x in elements:
            if background - int(x[0]) > 10 or background - int(x[0]) < -10:
                    watermark = int(x[0])
                    break

    for x_arr in im_array:
        for i, pixel in enumerate(x_arr):
            if int(pixel) > int(watermark):
                x_arr[i] = 255
                total_white_pixel += 1
            else:
                x_arr[i] = 0
    f3 = Image.fromarray(im_array)
    f3.save('filterred.jpg')
    return f3


def main():
    filter_pixels(sys.argv[1], sys.argv[2])


if __name__ == "__main__":
    main()
