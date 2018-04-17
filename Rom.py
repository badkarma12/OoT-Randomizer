import io
import hashlib
import logging
import os
import struct
import random

from Utils import local_path
from Items import ItemFactory, item_data
from TextArray import text_array


JAP10HASH = '03a63945398191337e896e5771f77173'
RANDOMIZERBASEHASH = 'dc5840f0d1ef7b51009c5625a054b3dd'


class LocalRom(object):

    def __init__(self, file, patch=True):
        with open(file, 'rb') as stream:
            self.buffer = read_rom(stream)
        if patch:
            self.patch_base_rom()

    def write_byte(self, address, value):
        self.buffer[address] = value

    def write_bytes(self, startaddress, values):
        for i, value in enumerate(values):
            self.write_byte(startaddress + i, value)

    def write_int16_to_rom(self, address, value):
        self.write_bytes(address, int16_as_bytes(value))

    def write_int32_to_rom(self, address, value):
        self.write_bytes(address, int32_as_bytes(value))

    def write_to_file(self, file):
        with open(file, 'wb') as outfile:
            outfile.write(self.buffer)

    def patch_base_rom(self):
        # verify correct checksum of baserom
        basemd5 = hashlib.md5()
        basemd5.update(self.buffer)
#        if JAP10HASH != basemd5.hexdigest():
        if JAP10HASH != JAP10HASH:
            logging.getLogger('').warning('Supplied Base Rom does not match known MD5 for JAP(1.0) release. Will try to patch anyway.')

        # extend to 2MB
#        self.buffer.extend(bytearray([0x00] * (2097152 - len(self.buffer))))

        # verify md5
        patchedmd5 = hashlib.md5()
        patchedmd5.update(self.buffer)
#        if RANDOMIZERBASEHASH != patchedmd5.hexdigest():
        if RANDOMIZERBASEHASH != RANDOMIZERBASEHASH:
            raise RuntimeError('Provided Base Rom unsuitable for patching. Please provide a JAP(1.0) "Zelda no Densetsu - Kamigami no Triforce (Japan).sfc" rom to use as a base.')

def read_rom(stream):
    "Reads rom into bytearray"
    buffer = bytearray(stream.read())
    return buffer


def int16_as_bytes(value):
    value = value & 0xFFFF
    return [value & 0xFF, (value >> 8) & 0xFF]

def int32_as_bytes(value):
    value = value & 0xFFFFFFFF
    return [value & 0xFF, (value >> 8) & 0xFF, (value >> 16) & 0xFF, (value >> 24) & 0xFF]

def patch_rom(world, rom):

    # Can always return to youth
    rom.write_byte(0xCB6844, 0x35)
    rom.write_byte(0x253C0E2, 0x80)

    # Fix child shooting gallery reward to be static
    rom.write_bytes(0xD35EFC, [0x00, 0x00, 0x00, 0x00])

    # Fix target in woods reward to be static
    rom.write_bytes(0xE59CD4, [0x00, 0x00, 0x00, 0x00])

    # Fix GS rewards to be static
    rom.write_bytes(0xEA3934, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xEA3940 , [0x10, 0x00])

    # Fix horseback archery rewards to be static
    rom.write_byte(0xE12BA5, 0x00)
    rom.write_byte(0xE12ADD, 0x00)

    # Fix adult shooting gallery reward to be static
    rom.write_byte(0xD35F55, 0x00)

    # Fix deku theater rewards to be static
    rom.write_bytes(0xEC9A7C, [0x00, 0x00, 0x00, 0x00]) #Sticks
    rom.write_byte(0xEC9CD5, 0x00) #Nuts

    # Fix deku scrub who sells stick upgrade
    rom.write_bytes(0xDF8060, [0x00, 0x00, 0x00, 0x00])

    # Fix deku scrub who sells nut upgrade
    rom.write_bytes(0xDF80D4, [0x00, 0x00, 0x00, 0x00])

    # Fix rolling goron as child reward to be static
    rom.write_bytes(0xED2960, [0x00, 0x00, 0x00, 0x00])

    # Remove intro cutscene
    rom.write_bytes(0xB06BBA, [0x00, 0x00])

    # Remove locked door to Boss Key Chest in Fire Temple
    rom.write_byte(0x22D82B7, 0x3F)

    # Change Bombchu Shop check to Bomb Bag
    rom.write_byte(0x00C6CEDB, 0xA2)
    rom.write_byte(0x00C6CEDF, 0x18)

    # Change Bowling Alley check to Bomb Bag (Part 1)
    rom.write_bytes(0x00E2D716, [0xA6, 0x72])
    rom.write_byte(0x00E2D723, 0x18)

    # Change Bowling Alley check to Bomb Bag (Part 2)
    rom.write_bytes(0x00E2D892, [0xA6, 0x72])
    rom.write_byte(0x00E2D897, 0x18)

    # Change Bazaar check to Bomb Bag (Child?)
    rom.write_bytes(0x00C0082A, [0x00, 0x18])
    rom.write_bytes(0x00C0082C, [0x00, 0x0E, 0X74, 0X02])
    rom.write_byte(0x00C00833, 0xA0)

    # Change Bazaar check to Bomb Bag (Adult?)
    rom.write_bytes(0x00DF7A8E, [0x00, 0x18])
    rom.write_bytes(0x00DF7A90, [0x00, 0x0E, 0X74, 0X02])
    rom.write_byte(0x00DF7A97, 0xA0)

    # Change Goron Shop check to Bomb Bag
    rom.write_bytes(0x00C6ED86, [0x00, 0xA2])
    rom.write_bytes(0x00C6ED8A, [0x00, 0x18])

    # Fix Link the Goron to always work
    rom.write_bytes(0xED2FAC, [0x80, 0x6E, 0x0F, 0x18])
    rom.write_bytes(0xED2FEC, [0x24, 0x0A, 0x00, 0x00])
    rom.write_bytes(0xAE74D8, [0x24, 0x0E, 0x00, 0x00])

    # Fix King Zora Thawed to always work
    rom.write_bytes(0xE55C4C, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xE56290, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xE56298, [0x00, 0x00, 0x00, 0x00])

    # Fix Castle Courtyard to check for meeting Zelda, not Zelda fleeing, to block you
    rom.write_bytes(0xCD5E76, [0x0E, 0xDC])
    rom.write_bytes(0xCD5E12, [0x0E, 0xDC])

    # Speed Zelda's Letter scene
    rom.write_bytes(0x290E08E, [0x05, 0xF0])
    rom.write_bytes(0x2E8C108, [0xFF, 0xFF, 0xFF, 0xFF])
    rom.write_bytes(0xD12F76, [0x0E, 0xDC])

    # Speed Zelda escaping from Hyrule Castle
    Block_code = [0x00, 0x00, 0x00, 0x01, 0x00, 0x21, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02]
    rom.write_bytes(0x1FC0CF8, Block_code)

    # Speed learning Zelda's Lullaby
    Block_code = [0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x03, 0xE8, 0x00, 0x00, 0x00, 0x01, 0x00, 0x73, 0x00, 0x3B,
                  0x00, 0x3C, 0x00, 0x3C, 0x00, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00, 0x0C,
                  0x00, 0x17, 0x00, 0x00, 0x00, 0x10, 0x00, 0x02, 0x08, 0x8B, 0xFF, 0xFF,
                  0x00, 0xD4, 0x00, 0x11, 0x00, 0x20, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x2E8E900, Block_code)

    # Speed learning Sun's Song
    rom.write_bytes(0x332A4A6, [0x00, 0x3C])
    Block_code = [0x00, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00, 0x08, 0x00, 0x18, 0x00, 0x00,
                  0x00, 0x10, 0x00, 0x02, 0x08, 0x8B, 0xFF, 0xFF, 0x00, 0xD3, 0x00, 0x11,
                  0x00, 0x20, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x332A868, Block_code)

    # Speed learning Saria's Song
    rom.write_bytes(0x20B1736, [0x00, 0x3C])
    Block_code = [0x00, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00, 0x0C, 0x00, 0x15, 0x00, 0x00,
                  0x00, 0x10, 0x00, 0x02, 0x08, 0x8B, 0xFF, 0xFF, 0x00, 0xD1, 0x00, 0x11,
                  0x00, 0x20, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x20B1DA8, Block_code)
    rom.write_bytes(0x20B19C8, [0x00, 0x11, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00])
    Block_code = [0x00, 0x3E, 0x00, 0x11, 0x00, 0x20, 0x00, 0x00, 0x80, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0xD4, 0xFF, 0xFF, 0xF7, 0x31,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01, 0xD4]
    rom.write_bytes(0x20B19F8, Block_code)

    # Speed learning Epona's Song
    rom.write_bytes(0x29BEF68, [0x00, 0x5E, 0x00, 0x0A, 0x00, 0x0B, 0x00, 0x0B])
    Block_code = [0x00, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00, 0x02, 0x00, 0xD2, 0x00, 0x00,
                  0x00, 0x09, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0x00, 0x0A,
                  0x00, 0x3C, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x29BECB0, Block_code)

    # Speed learning Song of Time
    Block_code = [0x00, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00, 0x0C, 0x00, 0x19, 0x00, 0x00,
                  0x00, 0x10, 0x00, 0x02, 0x08, 0x8B, 0xFF, 0xFF, 0x00, 0xD5, 0x00, 0x11,
                  0x00, 0x20, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x252FC80, Block_code)
    rom.write_bytes(0x252FBA0, [0x00, 0x35, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0x1FC3B84, [0xFF, 0xFF, 0xFF, 0xFF])

    # Speed learning Song of Storms
    Block_code = [0x00, 0x00, 0x00, 0x0A, 0x00, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00, 0x02,
                  0x00, 0xD6, 0x00, 0x00, 0x00, 0x09, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF,
                  0xFF, 0xFF, 0x00, 0xBE, 0x00, 0xC8, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x3041084, Block_code)

    # Speed learning Minuet of Forest
    rom.write_bytes(0x20AFF86, [0x00, 0x3C])
    Block_code = [0x00, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x0F, 0x00, 0x00,
                  0x00, 0x10, 0x00, 0x02, 0x08, 0x8B, 0xFF, 0xFF, 0x00, 0x73, 0x00, 0x11,
                  0x00, 0x20, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x20B0800, Block_code)
    rom.write_bytes(0x20AFF90, [0x00, 0x11, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00])
    rom.write_bytes(0x20AFFC1, [0x00, 0x3E, 0x00, 0x11, 0x00, 0x20, 0x00, 0x00])

    # Speed learning Bolero of Fire
    rom.write_bytes(0x224B5D6, [0x00, 0x3C])
    Block_code = [0x00, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00, 0x0A, 0x00, 0x10, 0x00, 0x00,
                  0x00, 0x10, 0x00, 0x02, 0x08, 0x8B, 0xFF, 0xFF, 0x00, 0x74, 0x00, 0x11,
                  0x00, 0x20, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x224D7E8, Block_code)
    rom.write_bytes(0x224B5E0, [0x00, 0x11, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00])
    rom.write_bytes(0x224B611, [0x00, 0x3E, 0x00, 0x11, 0x00, 0x20, 0x00, 0x00])
    rom.write_bytes(0x224B7F8, [0x00, 0x00])
    rom.write_bytes(0x224B828, [0x00, 0x00])
    rom.write_bytes(0x224B858, [0x00, 0x00])
    rom.write_bytes(0x224B888, [0x00, 0x00])

    # Speed learning Serenade of Water
    rom.write_bytes(0x2BEB256, [0x00, 0x3C])
    Block_code = [0x00, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00, 0x10, 0x00, 0x11, 0x00, 0x00,
                  0x00, 0x10, 0x00, 0x02, 0x08, 0x8B, 0xFF, 0xFF, 0x00, 0x75, 0x00, 0x11,
                  0x00, 0x20, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x2BEC880, Block_code)
    rom.write_bytes(0x2BEB260, [0x00, 0x11, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00])
    rom.write_bytes(0x2BEB290, [0x00, 0x3E, 0x00, 0x11, 0x00, 0x20, 0x00, 0x00])
    rom.write_bytes(0x2BEB538, [0x00, 0x00])
    rom.write_bytes(0x2BEB548, [0x80, 0x00])
    rom.write_bytes(0x2BEB554, [0x80, 0x00])

    # Speed learning Nocturne of Shadow
    rom.write_bytes(0x1FFE460, [0x00, 0x2F, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])
    rom.write_bytes(0x1FFFDF6, [0x00, 0x3C])
    Block_code = [0x00, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00, 0x0E, 0x00, 0x13, 0x00, 0x00,
                  0x00, 0x10, 0x00, 0x02, 0x08, 0x8B, 0xFF, 0xFF, 0x00, 0x77, 0x00, 0x11,
                  0x00, 0x20, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x2000FD8, Block_code)
    rom.write_bytes(0x2000131, [0x00, 0x32, 0x00, 0x3A, 0x00, 0x3B, 0x00, 0x3B])

    # Speed learning Requiem of Spirit
    rom.write_bytes(0x218AF16, [0x00, 0x3C])
    Block_code = [0x00, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00, 0x08, 0x00, 0x12, 0x00, 0x00,
                  0x00, 0x10, 0x00, 0x02, 0x08, 0x8B, 0xFF, 0xFF, 0x00, 0x76, 0x00, 0x11,
                  0x00, 0x20, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x218C574, Block_code)
    rom.write_bytes(0x218B480, [0x00, 0x30, 0x00, 0x3A, 0x00, 0x3B, 0x00, 0x3B])
    Block_code = [0x00, 0x11, 0x00, 0x00, 0x00, 0x10, 0x00, 0x00, 0x40, 0x00, 0x00, 0x00,
                  0xFF, 0xFF, 0xFA, 0xF9, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x01,
                  0xFF, 0xFF, 0xFA, 0xF9, 0x00, 0x00, 0x00, 0x08, 0x00, 0x00, 0x00, 0x01,
                  0x0F, 0x67, 0x14, 0x08, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01]
    rom.write_bytes(0x218AF20, Block_code)
    rom.write_bytes(0x218AF50, [0x00, 0x3E, 0x00, 0x11, 0x00, 0x20, 0x00, 0x00])

    # Speed learning Prelude of Light
    rom.write_bytes(0x252FD26, [0x00, 0x3C])
    Block_code = [0x00, 0x00, 0x00, 0x13, 0x00, 0x00, 0x00, 0x0E, 0x00, 0x14, 0x00, 0x00,
                  0x00, 0x10, 0x00, 0x02, 0x08, 0x8B, 0xFF, 0xFF, 0x00, 0x78, 0x00, 0x11,
                  0x00, 0x20, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x2531320, Block_code)
    rom.write_bytes(0x252FF24, [0x80, 0x00])

    # Speed scene after Deku Tree
    rom.write_bytes(0x2077E20, [0x00, 0x07, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])
    rom.write_bytes(0x2078A10, [0x00, 0x0E, 0x00, 0x1F, 0x00, 0x20, 0x00, 0x20])
    Block_code = [0x00, 0x80, 0x00, 0x00, 0x00, 0x1E, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF, 
                  0xFF, 0xFF, 0x00, 0x1E, 0x00, 0x28, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF, 0xFF]
    rom.write_bytes(0x2079570, Block_code)

    # Speed scene after Dodongo's Cavern
    rom.write_bytes(0x2221E88, [0x00, 0x0C, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0x2223308, [0x00, 0x81, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])

    # Speed scene after Jabu Jabu's Belly
    rom.write_bytes(0x2113340, [0x00, 0x0D, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0x2113C18, [0x00, 0x82, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])
    rom.write_bytes(0x21131D0, [0x00, 0x01, 0x00, 0x00, 0x00, 0x3C, 0x00, 0x3C])

    # Speed scene after Forest Temple
    rom.write_bytes(0xD4ED68, [0x00, 0x45, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0xD4ED78, [0x00, 0x3E, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])
    rom.write_bytes(0x207B9D4, [0xFF, 0xFF, 0xFF, 0xFF])

    # Speed scene after Fire Temple
    rom.write_bytes(0x2001848, [0x00, 0x1E, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])
    rom.write_bytes(0xD100B4, [0x00, 0x62, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0xD10134, [0x00, 0x3C, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])

    # Speed scene after Water Temple
    rom.write_bytes(0xD5A458, [0x00, 0x15, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0xD5A3A8, [0x00, 0x3D, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])
    rom.write_bytes(0x20D0D20, [0x00, 0x29, 0x00, 0xC7, 0x00, 0xC8, 0x00, 0xC8])

    # Speed scene after Shadow Temple
    rom.write_bytes(0xD13EC8, [0x00, 0x61, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0xD13E18, [0x00, 0x41, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])

    # Speed scene after Spirit Temple
    rom.write_bytes(0xD3A0A8, [0x00, 0x60, 0x00, 0x3B, 0x00, 0x3C, 0x00, 0x3C])
    rom.write_bytes(0xD39FF0, [0x00, 0x3F, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00])

    # Speed Nabooru defeat scene
    rom.write_bytes(0x2F5AF84, [0x00, 0x00, 0x00, 0x05])
    rom.write_bytes(0x2F5B378, [0x80, 0x00])
    rom.write_bytes(0x2F5B384, [0x80, 0x00])
    rom.write_bytes(0x2F5B4A4, [0x80, 0x00])
    rom.write_bytes(0x2F5B4B0, [0x80, 0x00])
    rom.write_bytes(0x2F5B568, [0x80, 0x00])
    rom.write_bytes(0x2F5B574, [0x80, 0x00])
    rom.write_bytes(0x2F5B630, [0x80, 0x00])
    rom.write_bytes(0x2F5B63C, [0x80, 0x00])
    rom.write_bytes(0x2F5B770, [0x80, 0x00])
    rom.write_bytes(0x2F5B77C, [0x80, 0x00])

    # Speed scene with all medallions
    rom.write_bytes(0x2512680, [0x00, 0x74, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])

    # Speed collapse of Ganon's Tower
    rom.write_bytes(0x33FB328, [0x00, 0x76, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])

    # Speed completion of the trials in Ganon's Castle
    rom.write_bytes(0x31A8090, [0x00, 0x6B, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02]) #Forest
    rom.write_bytes(0x31A9E00, [0x00, 0x6E, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02]) #Fire
    rom.write_bytes(0x31A8B18, [0x00, 0x6C, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02]) #Water
    rom.write_bytes(0x31A9430, [0x00, 0x6D, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02]) #Shadow
    rom.write_bytes(0x31AB200, [0x00, 0x70, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02]) #Spirit
    rom.write_bytes(0x31AA830, [0x00, 0x6F, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02]) #Light

    # Speed obtaining Fairy Ocarina
    rom.write_bytes(0x2151230, [0x00, 0x72, 0x00, 0x3C, 0x00, 0x3D, 0x00, 0x3D])
    Block_code = [0x00, 0x4A, 0x00, 0x00, 0x00, 0x3A, 0x00, 0x00, 0xFF, 0xFF, 0xFF, 0xFF,
                  0xFF, 0xFF, 0x00, 0x3C, 0x00, 0x81, 0xFF, 0xFF]
    rom.write_bytes(0x2151240, Block_code)
    rom.write_bytes(0x2150E20, [0xFF, 0xFF, 0xFA, 0x4C])

    # Speed Zelda Light Arrow cutscene
    rom.write_bytes(0x2531B40, [0x00, 0x28, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])
    rom.write_bytes(0x2533830, [0x00, 0x31, 0x03, 0x0D, 0x03, 0x0E, 0x03, 0x0E])

    # Speed Bridge of Light cutscene
    rom.write_bytes(0x292D644, [0x00, 0x00, 0x00, 0xA0])
    rom.write_bytes(0x292D680, [0x00, 0x02, 0x00, 0x0A, 0x00, 0x6C, 0x00, 0x00])
    rom.write_bytes(0x292D6E8, [0x00, 0x27])
    rom.write_bytes(0x292D718, [0x00, 0x32])
    rom.write_bytes(0x292D810, [0x00, 0x02, 0x00, 0x3C])
    rom.write_bytes(0x292D924, [0xFF, 0xFF, 0x00, 0x14, 0x00, 0x96, 0xFF, 0xFF])

    # Remove remaining owls
    rom.write_bytes(0x1FE30CE, [0x01, 0x4B])
    rom.write_bytes(0x1FE30DE, [0x01, 0x4B])
    rom.write_bytes(0x1FE30EE, [0x01, 0x4B])
    rom.write_bytes(0x205909E, [0x00, 0x3F])

    # Darunia won't dance
    rom.write_bytes(0x22769E4, [0xFF, 0xFF, 0xFF, 0xFF])

    # Zora moves quickly
    rom.write_bytes(0xE56924, [0x00, 0x00, 0x00, 0x00])

    # Speed Jabu Jabu swallowing Link
    rom.write_bytes(0xCA0784, [0x00, 0x18, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])

    # Ruto no longer points to Zora Sapphire
    rom.write_bytes(0xD03BAC, [0xFF, 0xFF, 0xFF, 0xFF])

    # Ruto never disappears from Jabu Jabu's Belly
    rom.write_byte(0xD01EA3, 0x00)

    # Speed up Epona race start
    rom.write_bytes(0x29BE984, [0xFF, 0xFF, 0xFF, 0xFF])

    # Speed up Epona escape
    rom.write_bytes(0x1FC8B36, [0x00, 0x2A])

    # Speed up draining the well
    rom.write_bytes(0xE0A010, [0x00, 0x2A, 0x00, 0x01, 0x00, 0x02, 0x00, 0x02])
    rom.write_bytes(0x2001110, [0x00, 0x2B, 0x00, 0xB7, 0x00, 0xB8, 0x00, 0xB8])

    # Speed up opening the royal tomb for both child and adult
    rom.write_bytes(0x2025026, [0x00, 0x01])
    rom.write_bytes(0x2023C86, [0x00, 0x01])
    rom.write_byte(0x2025159, 0x02)
    rom.write_byte(0x2023E19, 0x02)

    #Speed opening of Door of Time
    rom.write_bytes(0xE0A176, [0x00, 0x02])
    rom.write_bytes(0xE0A35A, [0x00, 0x01, 0x00, 0x02])

    # Poacher's Saw no longer messes up Deku Theater
    rom.write_bytes(0xAE72CC, [0x00, 0x00, 0x00, 0x00])

    # No more free sword for the kid from pedestal
    rom.write_bytes(0xAE577C, [0x80, 0xA4, 0x00, 0x68])
    rom.write_bytes(0xAE58F4, [0x00, 0x00, 0x00, 0x00])
    rom.write_bytes(0xAE5F74, [0x00, 0x00, 0x00, 0x00])

    # Prevent kokriri sword from being added to inventory on game load
    rom.write_bytes(0xBAED6C, [0x00, 0x00, 0x00, 0x00])

    # Speed text
    for address in text_array:
        rom.write_byte(address, 0x08)

    # DMA in extra code
    Block_code = [0xAF, 0xBF, 0x00, 0x1C, 0xAF, 0xA4, 0x01, 0x40, 0x3C, 0x05, 0x03, 0x48,
                  0x3C, 0x04, 0x80, 0x40, 0x0C, 0x00, 0x03, 0x7C, 0x24, 0x06, 0x10, 0x00,
                  0x0C, 0x10, 0x02, 0x00]
    rom.write_bytes(0xB17BB4, Block_code)
    Block_code = [0x3C, 0x02, 0x80, 0x12, 0x24, 0x42, 0xD2, 0xA0, 0x24, 0x0E, 0x01, 0x40,
                  0xAC, 0x2E, 0xE5, 0x00, 0x03, 0xE0, 0x00, 0x08, 0x00, 0x00, 0x00, 0x00]
    rom.write_bytes(0x3480800, Block_code)
    rom.write_bytes(0xD270, [0x03, 0x48, 0x00, 0x00, 0x03, 0x48, 0x10, 0x00, 0x03, 0x48, 0x00, 0x00])

    # Fix checksum (Thanks Nintendo)
    Block_code = [0x93, 0x5E, 0x0E, 0x5B, 0xDA, 0x41, 0x6D, 0x4D]
    rom.write_bytes(0x10, Block_code)

    # Set hooks for various code
    rom.write_bytes(0xBE9AC0, [0x0C, 0x10, 0x00, 0x00]) #Progressive Items Text Hook
    rom.write_bytes(0xBE9AE0, [0x0C, 0x10, 0x00, 0x81]) #Progressive Items Item ID Hook
    rom.write_bytes(0xBCECB4, [0x08, 0x10, 0x00, 0xFF, 0x03, 0x19, 0x10, 0x21]) #Progressive Items Graphic ID Hook
    rom.write_bytes(0xBDA26C, [0x0C, 0x22, 0x9E, 0xF0]) #Progressive Items Object Hook, mechanics of parameter bizarre, chests
    rom.write_bytes(0xBDA0E0, [0x0C, 0x22, 0x9E, 0xF0]) #Progressive Items Object Hook, mechanics of parameter bizarre, NPCs
#    rom.write_bytes(0xBD6C94, [0x0C, 0x22, 0x9E, 0xF0]) #Progressive Items Object Hook, unsure where this case is called
    rom.write_bytes(0xB06C2C, [0x0C, 0x10, 0x01, 0x80]) #Save Writing Hook

    # Progressive Items (Text)
    Block_code = [0x90, 0x45, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00, 0x25, 0x4A, 0x00, 0x4F,
                  0x15, 0x45, 0x00, 0x08, 0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12,
                  0x91, 0x6B, 0xA6, 0x4D, 0x25, 0x4A, 0x00, 0xFF, 0x15, 0x4B, 0x00, 0x03,
                  0x31, 0x4A, 0x00, 0x00, 0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x36,
                  0x25, 0x4A, 0x00, 0x5A, 0x15, 0x45, 0x00, 0x0C, 0x31, 0x4A, 0x00, 0x00,
                  0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x73, 0x31, 0x6B, 0x00, 0x18,
                  0x15, 0x4B, 0x00, 0x03, 0x25, 0x4A, 0x00, 0x08, 0x30, 0xA5, 0x00, 0x00,
                  0x24, 0xA5, 0x00, 0x58, 0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00,
                  0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x59, 0x25, 0x4A, 0x00, 0x5C,
                  0x15, 0x45, 0x00, 0x0C, 0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12,
                  0x91, 0x6B, 0xA6, 0x73, 0x31, 0x6B, 0x00, 0xC0, 0x15, 0x4B, 0x00, 0x03,
                  0x25, 0x4A, 0x00, 0x40, 0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x79,
                  0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00, 0x30, 0xA5, 0x00, 0x00,
                  0x24, 0xA5, 0x00, 0x5B, 0x25, 0x4A, 0x00, 0xCE, 0x15, 0x45, 0x00, 0x08,
                  0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x72,
                  0x31, 0x6B, 0x00, 0x06, 0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00,
                  0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0xCD, 0x25, 0x4A, 0x00, 0x5F,
                  0x15, 0x45, 0x00, 0x08, 0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12,
                  0x91, 0x6B, 0xA6, 0x72, 0x31, 0x6B, 0x00, 0x30, 0x15, 0x4B, 0x00, 0x03,
                  0x31, 0x4A, 0x00, 0x00, 0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x5E,
                  0x25, 0x4A, 0x00, 0x90, 0x15, 0x45, 0x00, 0x09, 0x31, 0x4A, 0x00, 0x00,
                  0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x71, 0x31, 0x6B, 0x00, 0x06,
                  0x25, 0x4A, 0x00, 0x04, 0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00,
                  0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x91, 0x25, 0x4A, 0x00, 0xA7,
                  0x15, 0x45, 0x00, 0x09, 0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12,
                  0x91, 0x6B, 0xA6, 0x71, 0x31, 0x6B, 0x00, 0x30, 0x25, 0x4A, 0x00, 0x20,
                  0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00, 0x30, 0xA5, 0x00, 0x00,
                  0x24, 0xA5, 0x00, 0xA8, 0x25, 0x4A, 0x00, 0x6C, 0x15, 0x45, 0x00, 0x0C,
                  0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x72,
                  0x31, 0x6B, 0x00, 0xC0, 0x15, 0x4B, 0x00, 0x03, 0x25, 0x4A, 0x00, 0x40,
                  0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x30, 0x15, 0x4B, 0x00, 0x03,
                  0x31, 0x4A, 0x00, 0x00, 0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x07,
                  0x25, 0x4A, 0x00, 0x57, 0x15, 0x45, 0x00, 0x0C, 0x31, 0x4A, 0x00, 0x00,
                  0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x73, 0x31, 0x6B, 0x00, 0x03,
                  0x15, 0x4B, 0x00, 0x03, 0x25, 0x4A, 0x00, 0x01, 0x30, 0xA5, 0x00, 0x00,
                  0x24, 0xA5, 0x00, 0x31, 0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00,
                  0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x56, 0x03, 0xE0, 0x00, 0x08]
    rom.write_bytes(0x3480000, Block_code)

    # Progressive Items (Item IDs)
    Block_code = [0x00, 0x00, 0x00, 0x00, 0x31, 0x4A, 0x00, 0x00, 0x25, 0x4A, 0x00, 0x0B,
                  0x15, 0x45, 0x00, 0x08, 0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12,
                  0x91, 0x6B, 0xA6, 0x4D, 0x25, 0x4A, 0x00, 0xFF, 0x15, 0x4B, 0x00, 0x03,
                  0x31, 0x4A, 0x00, 0x00, 0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x0A,
                  0x25, 0x4A, 0x00, 0x4F, 0x15, 0x45, 0x00, 0x0C, 0x31, 0x4A, 0x00, 0x00,
                  0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x73, 0x31, 0x6B, 0x00, 0x18,
                  0x15, 0x4B, 0x00, 0x03, 0x25, 0x4A, 0x00, 0x08, 0x30, 0xA5, 0x00, 0x00,
                  0x24, 0xA5, 0x00, 0x4D, 0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00,
                  0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x4E, 0x25, 0x4A, 0x00, 0x52,
                  0x15, 0x45, 0x00, 0x0C, 0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12,
                  0x91, 0x6B, 0xA6, 0x73, 0x31, 0x6B, 0x00, 0xC0, 0x15, 0x4B, 0x00, 0x03,
                  0x25, 0x4A, 0x00, 0x40, 0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x50,
                  0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00, 0x30, 0xA5, 0x00, 0x00,
                  0x24, 0xA5, 0x00, 0x51, 0x25, 0x4A, 0x00, 0x54, 0x15, 0x45, 0x00, 0x08,
                  0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x72,
                  0x31, 0x6B, 0x00, 0x06, 0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00,
                  0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x53, 0x25, 0x4A, 0x00, 0x57,
                  0x15, 0x45, 0x00, 0x08, 0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12,
                  0x91, 0x6B, 0xA6, 0x72, 0x31, 0x6B, 0x00, 0x30, 0x15, 0x4B, 0x00, 0x03,
                  0x31, 0x4A, 0x00, 0x00, 0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x56,
                  0x25, 0x4A, 0x00, 0x98, 0x15, 0x45, 0x00, 0x09, 0x31, 0x4A, 0x00, 0x00,
                  0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x71, 0x31, 0x6B, 0x00, 0x06,
                  0x25, 0x4A, 0x00, 0x04, 0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00,
                  0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x99, 0x25, 0x4A, 0x00, 0x9A,
                  0x15, 0x45, 0x00, 0x09, 0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12,
                  0x91, 0x6B, 0xA6, 0x71, 0x31, 0x6B, 0x00, 0x30, 0x25, 0x4A, 0x00, 0x20,
                  0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00, 0x30, 0xA5, 0x00, 0x00,
                  0x24, 0xA5, 0x00, 0x9B, 0x25, 0x4A, 0x00, 0x49, 0x15, 0x45, 0x00, 0x0C,
                  0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x72,
                  0x31, 0x6B, 0x00, 0xC0, 0x15, 0x4B, 0x00, 0x03, 0x25, 0x4A, 0x00, 0x40,
                  0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x06, 0x15, 0x4B, 0x00, 0x03,
                  0x31, 0x4A, 0x00, 0x00, 0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x48,
                  0x25, 0x4A, 0x00, 0x4C, 0x15, 0x45, 0x00, 0x0C, 0x31, 0x4A, 0x00, 0x00,
                  0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x73, 0x31, 0x6B, 0x00, 0x03,
                  0x15, 0x4B, 0x00, 0x03, 0x25, 0x4A, 0x00, 0x01, 0x30, 0xA5, 0x00, 0x00,
                  0x24, 0xA5, 0x00, 0x03, 0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00,
                  0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0x4B, 0x08, 0x01, 0xBF, 0x73]
    rom.write_bytes(0x3480200, Block_code)

    # Progressive Items (Graphic IDs)
    Block_code = [0x80, 0x43, 0x00, 0x02, 0x31, 0x4A, 0x00, 0x00, 0x25, 0x4A, 0x00, 0x2E,
                  0x15, 0x43, 0x00, 0x08, 0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12,
                  0x91, 0x6B, 0xA6, 0x4D, 0x25, 0x4A, 0x00, 0xFF, 0x15, 0x4B, 0x00, 0x03,
                  0x31, 0x4A, 0x00, 0x00, 0x30, 0x63, 0x00, 0x00, 0x24, 0x63, 0x00, 0x2D,
                  0x25, 0x4A, 0x00, 0x1A, 0x15, 0x43, 0x00, 0x0C, 0x31, 0x4A, 0x00, 0x00,
                  0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x73, 0x31, 0x6B, 0x00, 0x18,
                  0x15, 0x4B, 0x00, 0x03, 0x25, 0x4A, 0x00, 0x08, 0x30, 0x63, 0x00, 0x00,
                  0x24, 0x63, 0x00, 0x18, 0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00,
                  0x30, 0x63, 0x00, 0x00, 0x24, 0x63, 0x00, 0x19, 0x25, 0x4A, 0x00, 0x4A,
                  0x15, 0x43, 0x00, 0x0C, 0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12,
                  0x91, 0x6B, 0xA6, 0x73, 0x31, 0x6B, 0x00, 0xC0, 0x15, 0x4B, 0x00, 0x03,
                  0x25, 0x4A, 0x00, 0x40, 0x30, 0x63, 0x00, 0x00, 0x24, 0x63, 0x00, 0x58,
                  0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00, 0x30, 0x63, 0x00, 0x00,
                  0x24, 0x63, 0x00, 0x49, 0x25, 0x4A, 0x00, 0x2B, 0x15, 0x43, 0x00, 0x08,
                  0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x72,
                  0x31, 0x6B, 0x00, 0x06, 0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00,
                  0x30, 0x63, 0x00, 0x00, 0x24, 0x63, 0x00, 0x2A, 0x25, 0x4A, 0x00, 0x23,
                  0x15, 0x43, 0x00, 0x08, 0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12,
                  0x91, 0x6B, 0xA6, 0x72, 0x31, 0x6B, 0x00, 0x30, 0x15, 0x4B, 0x00, 0x03,
                  0x31, 0x4A, 0x00, 0x00, 0x30, 0x63, 0x00, 0x00, 0x24, 0x63, 0x00, 0x22,
                  0x25, 0x4A, 0x00, 0x73, 0x15, 0x43, 0x00, 0x0C, 0x31, 0x4A, 0x00, 0x00,
                  0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x72, 0x31, 0x6B, 0x00, 0xC0,
                  0x15, 0x4B, 0x00, 0x03, 0x25, 0x4A, 0x00, 0x40, 0x30, 0x63, 0x00, 0x00,
                  0x24, 0x63, 0x00, 0x33, 0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00,
                  0x30, 0x63, 0x00, 0x00, 0x24, 0x63, 0x00, 0x6C, 0x25, 0x4A, 0x00, 0x17,
                  0x15, 0x43, 0x00, 0x0C, 0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12,
                  0x91, 0x6B, 0xA6, 0x73, 0x31, 0x6B, 0x00, 0x03, 0x15, 0x4B, 0x00, 0x03,
                  0x25, 0x4A, 0x00, 0x01, 0x30, 0x63, 0x00, 0x00, 0x24, 0x63, 0x00, 0x35,
                  0x15, 0x4B, 0x00, 0x03, 0x31, 0x4A, 0x00, 0x00, 0x30, 0x63, 0x00, 0x00,
                  0x24, 0x63, 0x00, 0x16, 0x08, 0x0E, 0x27, 0x2B]
    rom.write_bytes(0x34803FC, Block_code)

    # Progressive Items (Object IDs)
    Block_code = [0x31, 0x4A, 0x00, 0x00, 0x25, 0x4A, 0x01, 0x2D, 0x15, 0x45, 0x00, 0x08,
                  0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x73,
                  0x31, 0x6B, 0x00, 0xC0, 0x15, 0x4B, 0x00, 0x03, 0x25, 0x4A, 0x00, 0x00,
                  0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x01, 0x47, 0x25, 0x4A, 0x01, 0x7B,
                  0x15, 0x45, 0x00, 0x08, 0x31, 0x4A, 0x00, 0x00, 0x3C, 0x0B, 0x80, 0x12,
                  0x91, 0x6B, 0xA6, 0x72, 0x31, 0x6B, 0x00, 0xC0, 0x15, 0x4B, 0x00, 0x03,
                  0x25, 0x4A, 0x00, 0x00, 0x30, 0xA5, 0x00, 0x00, 0x24, 0xA5, 0x00, 0xE7,
                  0x25, 0x4A, 0x00, 0xBE, 0x15, 0x45, 0x00, 0x08, 0x31, 0x4A, 0x00, 0x00,
                  0x3C, 0x0B, 0x80, 0x12, 0x91, 0x6B, 0xA6, 0x73, 0x31, 0x6B, 0x00, 0x03,
                  0x15, 0x4B, 0x00, 0x03, 0x25, 0x4A, 0x00, 0x00, 0x30, 0xA5, 0x00, 0x00,
                  0x24, 0xA5, 0x00, 0xE9, 0x08, 0x0E, 0x46, 0x43]
    rom.write_bytes(0x3480564, Block_code)

    # Write Initial Save File
    Block_code = [0xA2, 0x28, 0x80, 0x20, 0x24, 0x05, 0x80, 0x02, 0x24, 0x0F, 0x00, 0x84,
                  0x24, 0x18, 0x00, 0x01, 0x24, 0x19, 0x00, 0x08, 0x24, 0x08, 0x00, 0x80,
                  0xA6, 0x25, 0x00, 0xD8, 0xA2, 0x2F, 0x00, 0xDA, 0xA2, 0x38, 0x01, 0x65,
                  0xA2, 0x39, 0x09, 0xB6, 0xA2, 0x28, 0x0A, 0x24, 0xA2, 0x38, 0x0A, 0xCE,
                  0xA2, 0x28, 0x0A, 0xCF, 0xA2, 0x28, 0x0A, 0xE8, 0x24, 0x05, 0x00, 0x20,
                  0xA2, 0x25, 0x0B, 0x3F, 0xA2, 0x28, 0x0E, 0xDC, 0xA2, 0x25, 0x0E, 0xDD,
                  0xA2, 0x25, 0x0E, 0xED, 0xA2, 0x38, 0x0E, 0xF9, 0xA2, 0x25, 0x00, 0xA7,
                  0xA2, 0x28, 0x0E, 0xE0, 0xA2, 0x38, 0x02, 0x0E, 0x24, 0x05, 0x01, 0xFF,
                  0x24, 0x0F, 0x01, 0xFB, 0x24, 0x18, 0x07, 0xFF, 0x24, 0x19, 0x00, 0x04,
                  0x24, 0x08, 0x00, 0x30, 0xA6, 0x25, 0x0E, 0xE2, 0xA6, 0x2F, 0x0E, 0xE8,
                  0xA6, 0x38, 0x0E, 0xEA, 0xA2, 0x28, 0x0E, 0xE7, 0xA2, 0x39, 0x0F, 0x1A,
                  0x24, 0x08, 0x10, 0x20, 0x24, 0x19, 0x00, 0x2C, 0x24, 0x18, 0x00, 0x49,
                  0x24, 0x0F, 0x00, 0x02, 0x24, 0x05, 0x00, 0x40, 0xA6, 0x28, 0x0E, 0xD4,
                  0xA2, 0x39, 0x00, 0x81, 0xA2, 0x38, 0x00, 0xF6, 0xA2, 0x2F, 0x00, 0x3F,
                  0xA2, 0x25, 0x0A, 0x42, 0x92, 0x25, 0x0E, 0xDC, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0xA2, 0x25, 0x0E, 0xDC, 0x00, 0x00, 0x00, 0x00,
                  0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x03, 0xE0, 0x00, 0x08]
    rom.write_bytes(0x3480600, Block_code)

    # Set up Rainbow Bridge conditions
    if world.bridge == 'medallions':
        Block_code = [0x80, 0xEA, 0x00, 0xA7, 0x24, 0x01, 0x00, 0x3F,
                      0x31, 0x4A, 0x00, 0x3F, 0x00, 0x00, 0x00, 0x00]
        rom.write_bytes(0xE2B454, Block_code)
    elif world.bridge == 'open':
        rom.write_bytes(0x34806B0, [0x34, 0xA5, 0x00, 0x20])

    if world.open_forest:
        rom.write_byte(0x2081148, 0x80)
        rom.write_bytes(0x34806BC, [0x92, 0x25, 0x0E, 0xD5, 0x34, 0xA5, 0x00, 0x10, 0xA2, 0x25, 0x0E, 0xD5])

    if world.open_door_of_time:
        rom.write_bytes(0x34806B4, [0x34, 0xA5, 0x00, 0x08])

    # patch items
    for location in world.get_locations():
        itemid = location.item.code
        locationaddress = location.address
        secondaryaddress = location.address2

        if itemid is None or location.address is None:
            continue
        if location.type == 'Special':
            if location.name == 'Treasure Chest Game':
                rom.write_bytes(locationaddress, item_data[location.item.name])
            else:
                rom.write_byte(locationaddress, item_data[location.item.name][0])
                rom.write_byte(secondaryaddress, item_data[location.item.name][3])
        elif location.type == 'Song':
            rom.write_byte(locationaddress, itemid)
            itemid = itemid + 0x0D
            rom.write_byte(secondaryaddress, itemid)
            if location.name == 'Impa at Castle':
                impa_fix = 0x65 - location.item.index
                rom.write_byte(0xD12ECB, impa_fix)
                impa_fix = 0x8C34 - (location.item.index * 4)
                impa_fix_high = impa_fix >> 8
                impa_fix_low = impa_fix & 0x00FF
                rom.write_bytes(0xB063FE, [impa_fix_high, impa_fix_low])
                rom.write_byte(0x2E8E931, item_data[location.item.name]) #Fix text box
            elif location.name == 'Song from Malon':
                malon_fix = 0x8C34 - (location.item.index * 4)
                malon_fix_high = malon_fix >> 8
                malon_fix_low = malon_fix & 0x00FF
                rom.write_bytes(0xD7E142, [malon_fix_high, malon_fix_low])
#                rom.write_bytes(0xD7E8D6, [malon_fix_high, malon_fix_low]) # I don't know what this does, may be useful?
                rom.write_bytes(0xD7E786, [malon_fix_high, malon_fix_low])
                rom.write_byte(0x29BECB9, item_data[location.item.name]) #Fix text box
            elif location.name == 'Song from Composer Grave':
                sun_fix = 0x8C34 - (location.item.index * 4)
                sun_fix_high = sun_fix >> 8
                sun_fix_low = sun_fix & 0x00FF
                rom.write_bytes(0xE09F66, [sun_fix_high, sun_fix_low])
                rom.write_byte(0x332A87D, item_data[location.item.name]) #Fix text box
            elif location.name == 'Song from Saria':
                saria_fix = 0x65 - location.item.index
                rom.write_byte(0xE2A02B, saria_fix)
                saria_fix = 0x8C34 - (location.item.index * 4)
                saria_fix_high = saria_fix >> 8
                saria_fix_low = saria_fix & 0x00FF
                rom.write_bytes(0xE29382, [saria_fix_high, saria_fix_low])
                rom.write_byte(0x20B1DBD, item_data[location.item.name]) #Fix text box
            elif location.name == 'Song from Ocarina of Time':
                rom.write_byte(0x252FC95, item_data[location.item.name]) #Fix text box
            elif location.name == 'Song at Windmill':
                windmill_fix = 0x65 - location.item.index
                rom.write_byte(0xE42ABF, windmill_fix)
                rom.write_byte(0x3041091, item_data[location.item.name]) #Fix text box
            elif location.name == 'Sheik Forest Song':
                minuet_fix = 0x65 - location.item.index
                rom.write_byte(0xC7BAA3, minuet_fix)
                rom.write_byte(0x20B0815, item_data[location.item.name]) #Fix text box
            elif location.name == 'Sheik at Temple':
                prelude_fix = 0x65 - location.item.index
                rom.write_byte(0xC8060B, prelude_fix)
                rom.write_byte(0x2531335, item_data[location.item.name]) #Fix text box
            elif location.name == 'Sheik in Crater':
                bolero_fix = 0x65 - location.item.index
                rom.write_byte(0xC7BC57, bolero_fix)
                rom.write_byte(0x224D7FD, item_data[location.item.name]) #Fix text box
            elif location.name == 'Sheik in Ice Cavern':
                serenade_fix = 0x65 - location.item.index
                rom.write_byte(0xC7BD77, serenade_fix)
                rom.write_byte(0x2BEC895, item_data[location.item.name]) #Fix text box
            elif location.name == 'Sheik in Kakariko':
                nocturne_fix = 0x65 - location.item.index
                rom.write_byte(0xAC9A5B, nocturne_fix)
                rom.write_byte(0x2000FED, item_data[location.item.name]) #Fix text box
            elif location.name == 'Sheik at Colossus':
                rom.write_byte(0x218C589, item_data[location.item.name]) #Fix text box
        elif location.type == 'NPC':
            rom.write_byte(locationaddress, location.item.index)
            if secondaryaddress is not None:
                rom.write_byte(secondaryaddress, location.item.index)
        else:
            locationdefault = location.default & 0xF01F
            itemid = itemid | locationdefault
            itemidhigh = itemid >> 8
            itemidlow = itemid & 0x00FF

            rom.write_bytes(locationaddress, [itemidhigh, itemidlow])
            if secondaryaddress is not None:
                rom.write_bytes(secondaryaddress, [itemidhigh, itemidlow])

    return rom