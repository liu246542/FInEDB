#!/usr/bin/python3

import random
from .tools import prf_256, hash_to_fixsize, boxr


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
