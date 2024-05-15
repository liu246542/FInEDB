#!/usr/bin/python3

import random
from .tools import prf_256, hash_to_fixsize, bxor


class TSet(object):
    """
    docstring for TSet
    """

    def __init__(self):
        self.B = 256

    def __count_S__(self, index_dict, K):
        pos_record = {}
        for label in index_dict.keys():
            stag = prf_256(K, label)
            for i, _ in enumerate(index_dict.get(label)):
                pos_b = hash_to_fixsize(1, stag + str(i).encode())
                counter = pos_record.setdefault(pos_b, 0)
                counter += 1
                pos_record[pos_b] = counter
        return max([pos_record[x] for x in pos_record])

    def setup(self, index_dict, K):
        self.S = self.__count_S__(index_dict, K)
        free_list = [list(range(self.S)) for i in range(self.B)]
        emm = [[(0, 0) for j in range(self.S)] for i in range(self.B)]

        for label in index_dict.keys():
            stag = prf_256(K, label)
            value = index_dict.get(label)
            for i, j in enumerate(value):
                # j \xor mask_k
                stag_count = stag + str(i).encode()
                b = int.from_bytes(hash_to_fixsize(1, stag_count),
                                   byteorder="big")
                L = hash_to_fixsize(256, stag_count)
                mask_k = hash_to_fixsize(len(j) + 1, stag_count)

                b_pos = random.choice(free_list[b])
                free_list[b].remove(b_pos)
                beta = b"1"
                if i == len(value) - 1:
                    beta = b"0"
                c = bxor(mask_k, beta + j)
                emm[b][b_pos] = (L, c)
        return emm

    def gen_token(self, label, K):
        return prf_256(K, label)
