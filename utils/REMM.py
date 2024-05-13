#!/usr/bin/python3

import random
from .tools import prf_256, hash_to_fixsize, bxor


class REMM(object):
    """
    docstring for REMM
    B, the length of TSet
    S, the length of each element in TSet
    K_T, the secret key for TSet
    """

    def __init__(self):
        self.B = 256

    def __count_S__(self, index_dict, K_T):
        pos_record = {}
        for label in index_dict.keys():
            stag = prf_256(K_T, label)
            for i, _ in enumerate(index_dict.get(label)):
                pos_b = hash_to_fixsize(1, stag + str(i).encode())
                counter = pos_record.setdefault(pos_b, 0)
                counter += 1
                pos_record[pos_b] = counter
        return max([pos_record[x] for x in pos_record])

    def setup(self, index_dict, K_T):
        self.S = self.__count_S__(index_dict, K_T)
        free_list = [list(range(self.S)) for i in range(self.B)]
        self.emm = [[(0, 0) for j in range(self.S)] for i in range(self.B)]

        for label in index_dict.keys():
            stag = prf_256(K_T, label)
            value = index_dict.get(label)
            # if len(value) == 1 and type(value[0]) is list
            if isinstance(value[0], list):
                b = int.from_bytes(hash_to_fixsize(1, stag),
                                   byteorder="big")
                L = hash_to_fixsize(256, stag)
                c = value[0]

                b_pos = random.choice(free_list[b])
                free_list[b].remove(b_pos)
                # print(free_list)
                self.emm[b][b_pos] = (L, c)
            else:
                for i, j in enumerate(value):
                    enc_value = prf_256(K_T, j)
                    stag_count = stag + str(i).encode()
                    b = int.from_bytes(hash_to_fixsize(1, stag_count),
                                       byteorder="big")
                    L = hash_to_fixsize(256, stag_count)
                    K = hash_to_fixsize(len(enc_value) + 1, stag_count)
                    beta = b"1"
                    if i == len(value) - 1:
                        beta = b"0"
                    c = bxor(K, beta + enc_value)

                    b_pos = random.choice(free_list[b])
                    free_list[b].remove(b_pos)
                    self.emm[b][b_pos] = (L, c)
