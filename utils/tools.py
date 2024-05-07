#!/usr/bin/python3

import math
import hashlib
from queue import Queue, LifoQueue


def hash_to_fixsize(bytesize, content):
    # constrain the output's size (as =bytesize)
    if bytesize > 64:
        for_count = math.ceil(bytesize / 64)
        result_list = []
        last_length = bytesize
        for i in range(for_count):
            if i == for_count - 1:
                result_list.append(hash_to_fixsize(last_length, content))
            else:
                result_list.append(hash_to_fixsize(64, content))
                last_length -= 64
        return b"".join(result_list)
    hash_obj = hashlib.blake2b(digest_size=bytesize)
    hash_obj.update(content)
    return hash_obj.digest()


class BFF(object):
    """docstring for BFF

    """

    def __init__(self, N):
        assert N % 3 == 0
        self.segment_range = N / 3
        self.N = N

    def __hashfunc__(self, key, order):
        # order \gets {b"1", b"2", b"3"}
        pos = int.from_bytes(hash_to_fixsize(1, key + order), byteorder="big")
        pos_convert = pos % self.segment_range
        return pos_convert

    def construct(self, S):
        pass

    def calculate(self, poslist):
        pass


if __name__ == '__main__':
    a = hash_to_fixsize(1, b"cvcva3" + b"1")
    print(int.from_bytes(a, byteorder="big"))
