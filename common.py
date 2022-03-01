from typing import List, Optional, Union


DIR = 'D:\\Games\\GOG Galaxy\\Games\\Might and Magic 1\\'
MONS = DIR + 'MONPIX.DTA'
WALLS = DIR + 'WALLPIX.DTA'
EXE = DIR + 'MM.EXE'

RLEMARKER = b'{'


class ImageSlice:
    def __init__(self, w, h, x, y, name):
        self.x = x
        self.y = y
        self.w = w
        self.h = h
        self.name = name
        self.ex = x+w
        self.ey = y+h


WALLSLICES = [
    ImageSlice(32, 128, 0, 0, 'left1'),
    ImageSlice(40, 96, 32, 16, 'left2'),
    ImageSlice(24, 64, 72, 32, 'left3'),
    ImageSlice(16, 32, 96, 48, 'left4'),

    ImageSlice(32, 128, 192, 0, 'right1'),
    ImageSlice(40, 96, 152, 16, 'right2'),
    ImageSlice(24, 64, 128, 32, 'right3'),
    ImageSlice(16, 32, 112, 48, 'right4'),

    ImageSlice(176, 96, 224, 0, 'mid2'),
    ImageSlice(96, 64, 400, 0, 'mid3'),
    ImageSlice(48, 32, 400, 80, 'mid4'),
    ImageSlice(16, 16, 460, 80, 'mid5'),
]

MONSTERW = 104
MONSTERH = 96
MONSTERSLICES = [ImageSlice(MONSTERW, MONSTERH, 0, 0, '')]

SCREENW = 320
SCREENH = 200
SCREENSLICES = [ImageSlice(SCREENW, SCREENH, 0, 0, '')]


v = 0x55
a = 0xaa
f = 0xff
EGA = [0, 0, 0, 0, 0, a, 0, a, 0, 0, a, a, a, 0, 0, a, 0, a, a, v, 0, a,
       a, a, v, v, v, v, v, f, v, f, v, v, f, f, f, v, v, f, v, f, f, f, v, f, f, f]

CGA0 = [0, 0, 0, 0, a, 0, a, 0, 0, f, f, f]


def ztrim(b: bytes):
    return b.decode('ascii').strip()


def flags(n: int, flags: Union[str, List[str]], fail: Optional[str]) -> List[str]:
    j = 1
    r = []
    for fl in flags:
        if n & j:
            r.append(fl)
        elif fail:
            r.append(fail)
        j *= 2
    return r
