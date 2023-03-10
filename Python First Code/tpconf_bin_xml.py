#!/usr/bin/env python3

# Copyright 2018 Alain Ducharme
#
# This program is free software: you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program.  If not, see <http://www.gnu.org/licenses/>.
#
# Description:
# Command line utility to convert TP-Link router backup config files:
#   - conf.bin => decrypt, md5hash and uncompress => conf.xml
#   - conf.xml => compress, md5hash and encrypt   => conf.bin

import argparse
from hashlib import md5
from os import path
from struct import pack_into, unpack_from

from Crypto.Cipher import DES   # apt install python3-crypto (OR pip install pycryptodome ?)

__version__ = '0.2.1'

def compress(src):
    '''Compress buffer'''
    # Make sure last byte is NULL
    if src[-1]:
        src += b'\0'
    size = len(src)
    buffer_countdown = size
    hash_table = [0] * 0x2000
    dst = bytearray(0x8000)   # max compressed buffer size
    block16_countdown = 0x10  # 16 byte blocks
    block16_dict_bits = 0     # bits for dictionnary bytes

    def put_bit(bit):
        nonlocal block16_countdown, block16_dict_bits, d_p, d_pb
        if block16_countdown:
            block16_countdown -= 1
        else:
            pack_into('H', dst, d_pb, block16_dict_bits)
            d_pb = d_p
            d_p += 2
            block16_countdown = 0xF
        block16_dict_bits = (bit + (block16_dict_bits << 1)) & 0xFFFF

    def put_dict_ld(bits):
        ldb = bits >> 1
        while True:
            lb = (ldb - 1) & ldb
            if not lb:
                break
            ldb = lb
        put_bit(int(ldb & bits > 0))
        ldb = ldb >> 1
        while ldb:
            put_bit(1)
            put_bit(int(ldb & bits > 0))
            ldb = ldb >> 1
        put_bit(0)

    def hash_key(offset):
        b4 = src[offset:offset+4]
        hk = 0
        for b in b4[:3]:
            hk = (hk + b) * 0x13d
        return ((hk + b4[3]) & 0x1FFF)

    pack_into(packint, dst, 0, size)    # Store original size
    dst[4] = src[0]                     # Copy first byte
    buffer_countdown -= 1
    s_p = 1
    s_ph = 0
    d_pb = 5
    d_p = 7

    while buffer_countdown > 4:
        while s_ph < s_p:
            hash_table[hash_key(s_ph)] = s_ph
            s_ph += 1
        hit = hash_table[hash_key(s_p)]
        count = 0
        if hit:
            while True:
                if src[hit + count] != src[s_p + count]:
                    break
                count += 1
                if count == buffer_countdown:
                    break
            if count >= 4 or count == buffer_countdown:
                hit = s_p - hit
                put_bit(1)
                hit -= 1
                put_dict_ld(count - 2)
                put_dict_ld((hit >> 8) + 2)
                dst[d_p] = hit & 0xFF
                d_p += 1
                buffer_countdown -= count
                s_p += count
                continue
        put_bit(0)
        dst[d_p] = src[s_p]
        s_p += 1
        d_p += 1
        buffer_countdown -= 1
    while buffer_countdown:
        put_bit(0)
        dst[d_p] = src[s_p]
        s_p += 1
        d_p += 1
        buffer_countdown -= 1
    pack_into('H', dst, d_pb, (block16_dict_bits << block16_countdown) & 0xFFFF)

    padded = (d_p | 7) + 1 if d_p & 7 else d_p # multiple of 8 alignment

    return d_p, dst[:padded]    # size, padded_compressed_buffer

def uncompress(src):
    '''Uncompress buffer'''
    block16_countdown = 0 # 16 byte blocks
    block16_dict_bits = 0 # bits for dictionnary bytes

    def get_bit():
        nonlocal block16_countdown, block16_dict_bits, s_p
        if block16_countdown:
            block16_countdown -= 1
        else:
            block16_dict_bits = unpack_from('H', src, s_p)[0]
            s_p += 2
            block16_countdown = 0xF
        block16_dict_bits = block16_dict_bits << 1
        return 1 if block16_dict_bits & 0x10000 else 0 # went past bit

    def get_dict_ld():
        bits = 1
        while True:
            bits = (bits << 1) + get_bit()
            if not get_bit():
                break
        return bits

    size = unpack_from(packint, src, 0)[0]
    dst = bytearray(size)
    s_p = 4
    d_p = 0

    dst[d_p] = src[s_p]
    s_p += 1
    d_p += 1
    while d_p < size:
        if get_bit():
            num_chars = get_dict_ld() + 2
            msB = (get_dict_ld() - 2) << 8
            lsB = src[s_p]
            s_p += 1
            offset = d_p - (lsB + 1 + msB)
            for i in range(num_chars):
                # 1 by 1 ??? sometimes copying previously copied byte
                dst[d_p] = dst[offset]
                d_p += 1
                offset += 1
        else:
            dst[d_p] = src[s_p]
            s_p += 1
            d_p += 1
    return dst

def verify(src):
    # Try md5 hash excluding up to last 8 (padding) bytes
    if not any(src[:16] == md5(src[16:len(src)-i]).digest() for i in range(8)):
        print('ERROR: Bad file or could not decrypt file - MD5 hash check failed!')
        exit()

def check_size_endianness(src):
    global packint
    if unpack_from(packint, src)[0] > 0x20000:
        packint = '<I' if packint == '>I' else '>I'
        if unpack_from(packint, src)[0] > 0x20000:
            print('ERROR: compressed size too large for a TP-Link config file!')
            exit()
        print('OK: wrong endianness, automatically switching. (see -h)')

if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='TP-Link router config file processor.')
    parser.add_argument('infile', help='input file (e.g. conf.bin or conf.xml)')
    parser.add_argument('outfile', help='output file (e.g. conf.bin or conf.xml)')
    parser.add_argument('-l', '--littleendian', action='store_true',
                        help='Use little-endian (default: big-endian)')
    parser.add_argument('-n', '--newline', action='store_true',
                        help='Replace EOF NULL with newline (after uncompress)')
    parser.add_argument('-o', '--overwrite', action='store_true',
                        help='Overwrite output file')
    args = parser.parse_args()

    if path.getsize(args.infile) > 0x20000:
        print('ERROR: Input file too large for a TP-Link config file!')
        exit()
    if not args.overwrite and path.exists(args.outfile):
        print('ERROR: Output file exists, use -o to overwrite')
        exit()

    packint = '<I' if args.littleendian else '>I'

    key = b'\x47\x8D\xA5\x0B\xF9\xE3\xD2\xCF'
    crypto = DES.new(key, DES.MODE_ECB)

    with open(args.infile, 'rb') as f:
        src = f.read()

    if src.startswith(b'<?xml'):
        if b'W9980' in src:
            print('OK: W9980 XML file - hashing, compressing and encrypting???')
            md5hash = md5(src).digest()
            size, dst = compress(md5hash + src)
            with open(args.outfile, 'wb') as f:
                f.write(crypto.encrypt(bytes(dst)))
        else:
            print('OK: XML file - compressing, hashing and encrypting???')
            size, dst = compress(src)
            with open(args.outfile, 'wb') as f:
                f.write(crypto.encrypt(md5(dst[:size]).digest() + dst))
    else:
        xml = None
        # Assuming encrypted config file
        if len(src) & 7: # Encrypted file length must be multiple of 8
            print('ERROR: Wrong input file type!')
            exit()
        src = crypto.decrypt(src)
        if src[16:21] == b'<?xml':  # XML (not compressed?)
            verify(src)
            print('OK: BIN file decrypted, MD5 hash verified???')
            xml = src[16:]
        elif src[20:27] == b'<\0\0?xml':  # compressed XML (W9970)
            verify(src)
            src = src[16:]
            check_size_endianness(src)
            print('OK: BIN file decrypted, MD5 hash verified, uncompressing???')
            xml = uncompress(src)
        elif src[22:29] == b'<\0\0?xml':  # compressed XML (W9980)
            check_size_endianness(src)
            print('OK: BIN file decrypted, uncompressing???')
            dst = uncompress(src)
            verify(dst)
            print('OK: MD5 hash verified')
            xml = dst[16:]
        else:
            print('ERROR: Unrecognized file type!')
            exit()

        if args.newline:
            if xml[-1] == 0:    # NULL
                xml[-1] = 0xa   # LF
        with open(args.outfile, 'wb') as f:
            f.write(xml)
    print('Done.')
