#!/usr/bin/python3

from .tools import prf_256, hash_to_fixsize, bxor, gen_key, aes_enc


class STE():
    """
    docstring for STE
    """

    def __init__(self, SK):
        self.SK = SK
        # SK contains (K_1, K_2, K_3, K_4)

    def setup(self, index_dict):
        ctr = 1
        for label in index_dict.keys():
            K_temp = [gen_key(256) for i in range(2)]
            value = index_dict.get(label)
            for i, j in enumerate(value):
                pass
                # node =
                # if i == len(value) - 1:
