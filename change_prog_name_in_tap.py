#!/usr/bin/env python3
# -*- coding: utf-8 -*-

# from sys import argv
argv = ['', 'example.tap', 'example']

def change_prog_name_in_tap(fname, prj_name):
    assert(len(prj_name) <= 10)
    with open(fname, 'rb') as file:
        data = file.read()
        data = data.replace(b'boot      ',
                            bytes(prj_name.ljust(10), encoding='ascii'),
                            1)
        new_data = data[:20] + bytes([checksum(data)]) + data[21:]
    with open(fname, 'wb') as file:
        file.write(new_data)


def checksum(data):
    ans = 0
    for d in data[2:20]:
        ans ^= d
    return ans


if __name__ == '__main__':
    change_prog_name_in_tap(argv[1], argv[2])
