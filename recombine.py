from typing import List
from PIL import Image
from struct import pack
from glob import glob

from common import CGA0, MONSTERSLICES, RLEMARKER, SCREENSLICES, WALLSLICES, ImageSlice
from dump import dumpMulti


def encodeRun(d: bytes, rs: int):
    count = len(d) - rs
    if count > 3:
        value = d[rs]
        while count > 0:
            l = min(256, count)
            d = d[:rs] + RLEMARKER + bytes([l-1, value])
            count -= l
            rs += 3
    return d


def encodeRLE(raw: bytes):
    d = bytes()
    rs = None
    for i in raw:
        if i == RLEMARKER[0]:
            if rs != None:
                d = encodeRun(d, rs)
                rs = None
            d += RLEMARKER + bytes([0, i])
            continue
        b = bytes([i])
        if len(d) > 1:
            match = d[-1] == d[-2] and d[-1] == i
            if match:
                if rs == None:
                    rs = len(d) - 2
            else:
                if rs != None:
                    d = encodeRun(d, rs)
                    rs = None
        d += b
    if rs != None:
        d = encodeRun(d, rs)
    # print('encodeRLE:', len(raw), '->', len(d))
    return d


def encodeRLEImage(fn: str, pal: List[int], slices: List[ImageSlice]):
    img = Image.open(fn)
    data = list(img.getdata())
    raw = bytes()
    for s in slices:
        sd = bytes()
        for x in range(s.x, s.ex, 4):
            for y in range(s.y, s.ey):
                i = y * img.width + x
                b = data[i:i+4]
                byte = (b[0] << 6) + (b[1] << 4) + (b[2] << 2) + b[3]
                sd += bytes([byte])
        raw += encodeRLE(sd)
        # print('after', s.name, len(raw), 'bytes')
    return raw


def writeMulti(fn: str, pat: str, pal: List[int], slices: List[ImageSlice]):
    filenames = glob(pat)
    filenames.sort()
    headerSize = len(filenames) * 4
    offsets = []
    file = bytes()
    for component in filenames:
        print('Reading:', component)
        data = encodeRLEImage(component, pal, slices)
        dataSize = len(data)
        offsets.append(len(file))
        file += pack('h', dataSize) + data
    f = open(fn, 'wb')
    f.write(pack('h', headerSize))
    for o in offsets:
        f.write(pack('i', o))
    f.write(file)
    print('Wrote:', fn)


def writeScreen(fn: str, ifn: str, pal: List[int]):
    f = open(fn, 'wb')
    print('Reading:', ifn)
    data = encodeRLEImage(ifn, pal, SCREENSLICES)
    dataSize = len(data)
    f.write(pack('h', dataSize) + data)
    print('Wrote:', fn)


if __name__ == '__main__':
    writeMulti('WALLPIX.DTA', 'wall*.png', CGA0, WALLSLICES)
    writeMulti('MONPIX.DTA', 'mon*.png', CGA0, MONSTERSLICES)

    for n in range(10):
        writeScreen('SCREEN%d' % n, 'SCREEN%d.png' % n, CGA0)

    # dumpMulti('WALLPIX.DTA', 'redump\\wall%02d.png',
    #           1, CGA0, WALLSLICES, 496, 128)
    # dumpMulti('MONPIX.DTA', 'redump\\mon%02d.png',
    #           4, CGA0, MONSTERSLICES, MONSTERW, MONSTERH)
