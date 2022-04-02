from typing import BinaryIO, List, Tuple
from PIL import Image, ImageDraw
from struct import unpack

from common import CGA0, DIR, EXE, MONS, MONSTERH, MONSTERSLICES, MONSTERW, RLEMARKER, SCREENH, SCREENW, WALLS, WALLSLICES, ImageSlice, flags, ztrim


def decodeRLE(f: BinaryIO, size: int) -> bytes:
    buffer = bytes()
    eof = f.tell() + size
    while f.tell() < eof:
        b = f.read(1)
        if b == RLEMARKER:
            c = f.read(1)
            z = f.read(1)
            buffer += z * (c[0] + 1)
        else:
            buffer += b
    # print('decodeRLE:', size, '->', len(buffer))
    return buffer


def getImageData(buffer: bytes, start: int, w: int, h: int) -> Tuple[List[int], int]:
    d = [0] * w * h
    j = start
    x = 0
    y = 0
    while x < w and j < len(buffer):
        p1 = (buffer[j] & 0x03)
        p2 = (buffer[j] & 0x0C) >> 2
        p3 = (buffer[j] & 0x30) >> 4
        p4 = (buffer[j] & 0xC0) >> 6
        j += 1
        i = y * w + x
        d[i] = p4
        d[i+1] = p3
        d[i+2] = p2
        d[i+3] = p1
        y += 1
        if y >= h:
            y = 0
            x += 4
    return (d, j)


def getRLEImage(f: BinaryIO, pal: List[int], w: int, h: int) -> Image:
    size = unpack('h', f.read(2))[0]
    buffer = decodeRLE(f, size)
    img = Image.new('P', [w, h])
    (d, j) = getImageData(buffer, 0, w, h)
    img.putdata(d)
    img.putpalette(pal)
    return img


def dumpScreen(fn: str, pal: List[int], w: int, h: int):
    f = open(DIR + fn, 'rb')
    img = getRLEImage(f, pal, w, h)
    ofn = fn + '.png'
    print('writing:', ofn)
    img.save(ofn)


def dumpMulti(fn: str, fmt: str, count: int, pal: List[int], slices: List[ImageSlice], w: int, h: int):
    f = open(fn, 'rb')
    headerSize = unpack('h', f.read(2))[0]
    offsets = []
    while f.tell() < headerSize:
        offsets.append(unpack('i', f.read(4))[0])
    dataStart = f.tell()

    print('--- %s has %d images inside' % (fn, len(offsets)))
    for n in range(min(count, len(offsets))):
        f.seek(offsets[n] + dataStart)
        # print('image %d starts @%x' % (n, f.tell()))
        img = Image.new('P', [w, h])
        img.putpalette(pal)
        # dr = ImageDraw.Draw(img)
        size = unpack('h', f.read(2))[0]
        buf = decodeRLE(f, size)
        # print(size, 'expanded to', len(buf))
        j = 0
        for piece in slices:
            (data, j) = getImageData(buf, j, piece.w, piece.h)
            sub = Image.new('P', [piece.w, piece.h])
            sub.putdata(data)
            img.paste(sub, (piece.x, piece.y, piece.ex, piece.ey))
            # dr.rectangle((piece.x, piece.y, piece.ex-1, piece.ey-1), None, 4)
            # dr.text((piece.x, piece.y), piece.name, 4)
        ofn = fmt % (n+1)
        print('writing:', ofn)
        img.save(ofn)
        # print('image %d   ends @%x' % (n, f.tell()))


def dumpWallGfx(fmt='wall%02d.png'):
    dumpMulti(WALLS, fmt,
              18, CGA0, WALLSLICES, 496, 128)


def dumpMonsterGfx(fmt='mon%02d.png'):
    dumpMulti(MONS, fmt,
              800, CGA0, MONSTERSLICES, MONSTERW, MONSTERH)


def dumpScreenGfx():
    dumpScreen('SCREEN0', CGA0, SCREENW, SCREENH)
    dumpScreen('SCREEN1', CGA0, SCREENW, SCREENH)
    dumpScreen('SCREEN2', CGA0, SCREENW, SCREENH)
    dumpScreen('SCREEN3', CGA0, SCREENW, SCREENH)
    dumpScreen('SCREEN4', CGA0, SCREENW, SCREENH)
    dumpScreen('SCREEN5', CGA0, SCREENW, SCREENH)
    dumpScreen('SCREEN6', CGA0, SCREENW, SCREENH)
    dumpScreen('SCREEN7', CGA0, SCREENW, SCREENH)
    dumpScreen('SCREEN8', CGA0, SCREENW, SCREENH)
    dumpScreen('SCREEN9', CGA0, SCREENW, SCREENH)


ITEMEFFECTS = {
    0x00: 'Equip   ',
    0x01: '--------',
    0x15: 'INT  %+3d',
    0x17: 'MIGHT%+3d',
    0x19: 'PERS %+3d',
    0x1D: 'SPEED%+3d',
    0x1F: 'ACCY %+3d',
    0x21: 'LUCK %+3d',
    0x3C: 'AC   %+3d',
    0x58: 'MAGIC%+3d',
    0x5a: 'Fire %+3d',
    0x5c: 'Cold %+3d',
    0x5e: 'Elec %+3d',
    0x60: 'Elem %+3d',
    0x62: 'Fear %+3d',
    0x64: 'Poisn%+3d',
    0x66: 'Holy %+3d',
    0x6C: 'Thief%+3d',
    0xff: '*CURSED*',
}

WEARFLAGS = 'RSCAPKEG'


def dumpItems(ofn='items.txt'):
    fil = open(EXE, 'rb')
    fil.seek(0x19b2a)
    ofi = open(ofn, 'w')
    ofi.write('NAME           CANWEAR? EFFECT   ?? ?? ?? Money Dm Bo\n')
    for ix in range(255):
        raw = fil.read(24)
        name, wear, efftype, effbonus, d, e, f, cost, dmg, bonus = unpack(
            '>14sBBBBBBHBB', raw)
        eff = '??%02x/%02x ' % (efftype, effbonus)
        if efftype in ITEMEFFECTS:
            eff = ITEMEFFECTS[efftype]
            if '%' in eff:
                eff = eff % effbonus
        name = ztrim(name)
        canwear = ''.join(flags(255 - wear, WEARFLAGS, ' '))
        ofi.write('%-14s %-8s %s %02x %02x %02x %5d %2d %2d\n' %
                  (name, canwear, eff, d, e, f, cost, dmg, bonus))
    print('Wrote:', ofn)


def dumpEnemies(ofn='enemies.txt'):
    fil = open(EXE, 'rb')
    fil.seek(0x1b312)
    ofi = open(ofn, 'w')
    ofi.write(
        'NAME            ?? ??  HP-HP  AC Dmg AT SP EXP.. ?? Mag% ?? ?? ?? S% ?? ??\n')
    for ix in range(195):
        raw = fil.read(32)
        name, a, b, hp, ac, dmg, attacks, speed, exp, j, magicRes, l, m, n, spellChance, p, q = unpack(
            '15sBBBBBBBHBBBBBBBB', raw)
        name = ztrim(name)
        magicStar = ' '
        if magicRes & 128:
            magicRes -= 128
            magicStar = '*'
        ofi.write('%-15s %02x %02x %3d-%-3d %2d %3d %2d %2d %5d %02x %3d%s %02x %02x %02x %2d %02x %02x\n' %
                  (name, a, b, hp+1, hp+8, ac, dmg, attacks, speed, exp, j, magicRes, magicStar, l, m, n, spellChance, p, q))
    print('Wrote:', ofn)


if __name__ == '__main__':
    dumpItems()
    dumpEnemies()
    dumpWallGfx()
    dumpMonsterGfx()
    dumpScreenGfx()
