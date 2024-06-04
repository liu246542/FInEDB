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
        # self.emm = [[(0, 0) for j in range(self.S)] for i in range(self.B)]
        emm = [[(0, 0) for j in range(self.S)] for i in range(self.B)]

        for label in index_dict.keys():
            stag = prf_256(K_T, label)
            value = index_dict.get(label)
            if isinstance(value[0], list):
                # value[0] is BFF
                b = int.from_bytes(hash_to_fixsize(1, stag + b"0"),
                                   byteorder="big")
                L = hash_to_fixsize(256, stag + b"0")
                c = value[0]

                b_pos = random.choice(free_list[b])
                free_list[b].remove(b_pos)
                emm[b][b_pos] = (L, c)
            else:
                for i, j in enumerate(value):
                    # assert isinstance(j, str)
                    # print(type(j))
                    # print(i)
                    # print(label)
                    # print(value[0:3])
                    enc_value = prf_256(K_T, j)
                    if isinstance(j, bytes):
                        # enc_value = prf_256(K_T, j)
                        enc_value = j
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
                    emm[b][b_pos] = (L, c)

        return emm

    def query(self, emm, stag, recursive=1):
        res = []
        beta = b"1"
        i = 0
        while beta == b"1":
            stag_count = stag + str(i).encode()
            b = int.from_bytes(hash_to_fixsize(1, stag_count), byteorder="big")
            L = hash_to_fixsize(256, stag_count)
            #  --------------------------------------------
            check_flag = False
            for v in emm[b]:
                if v[0] == L and isinstance(v[1], list):
                    check_flag = True
                    res.append(v[1])
                    beta = b"0"
                    # return res
                    # return v[1]
                elif v[0] == L:
                    check_flag = True
                    K = hash_to_fixsize(len(v[1]), stag_count)
                    m = bxor(K, v[1])
                    # print(m)
                    beta = m[0:1]
                    tk_prime = m[1:]
                    # print(beta)

                    if recursive:
                        res.extend(self.query(emm, tk_prime))
                    else:
                        res.append(tk_prime)
                    # if beta == b"0":
                    # res.append(tk_prime)
                    # else:
                    # res.append(self.query(emm, tk_prime))
                    # res.append(tk_prime)
            if check_flag is False:
                raise RuntimeError("Wrong stag ?")
            #  --------------------------------------------
            i += 1
            # print(f"query at {i} times")
        return res
