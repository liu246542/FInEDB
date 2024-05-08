#!/usr/bin/python3

import math
import hashlib
import hmac
import json
import time
from charm.toolbox.symcrypto import SymmetricCryptoAbstraction
from charm.core.math.integer import randomBits
from queue import Queue, LifoQueue


def gen_key(key_length):
    assert key_length % 8 == 0
    temp_key = randomBits(key_length)
    return temp_key.to_bytes(int(key_length / 8), byteorder="big")


def prf_256(key, data):
    if not isinstance(data, bytes):
        data = bytes(data, "utf-8")
    h = hmac.new(key, data, hashlib.sha256)
    return h.digest()  # output's length is 32, i.e., 32 * 8 = 256


def aes_enc(key, plaintext):
    symcrypt = SymmetricCryptoAbstraction(key)
    # 暂不考虑压缩密文
    # cryptext = symcrypt.encrypt(plaintext)
    # CT = json.loads(cryptext)["CipherText"]
    # IV = json.loads(cryptext)["IV"]
    return symcrypt.encrypt(plaintext)


def bxor(b1, b2):
    if b1 == 0:
        return b2
    assert len(b1) == len(b2)
    return bytes(x ^ y for x, y in zip(b1, b2))


def hash_to_fixsize(bytesize, content):
    # constrain the output's size (as =bytesize)
    if not isinstance(content, bytes):
        content = bytes(content, "utf-8")
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

    def __init__(self):
        # assert N % 3 == 0
        # self.segment_range = N / 3
        # self.N = N
        self.segment_range = 24 / 3
        self.N = 24

    def __hashfunc__(self, key):
        # order \gets {b"1", b"2", b"3"}
        pos_list = []
        for i in range(3):
            pos = hash_to_fixsize(1, key + str(i))
            pos_int = int.from_bytes(pos, byteorder="big")
            pos_convert = pos_int % self.segment_range + i * self.segment_range
            pos_list.append(int(pos_convert))
        return pos_list

    def construct(self, dict_data, K_1, K_2, att_list, type_list):
        temp_dict = {}
        temp_hash = {}
        temp_p2lable = {}
        for i, att in enumerate(att_list):
            if type_list[i] == "1":
                # att + "SELECT" => enc(K_1, dict_data[att])
                label = att + "SELECT"
                value = bytes(aes_enc(K_1, str(dict_data[att])), "utf-8")
                assert len(value) == 97
                value = value.ljust(128, b"0")
                temp_dict.setdefault(label, value)

                label = att + "WHERE"
                value = prf_256(K_2, str(dict_data[att]))
                assert len(value) == 32
                value = value.ljust(128, b"0")
                temp_dict.setdefault(label, value)

        # Choose an appropriate size of BFF
        label_num = len(temp_dict.keys())
        if label_num < 24:
            self.N = 24
            self.segment_range = 24 / 3
        elif label_num < 48:
            self.N = 48
            self.segment_range = 48 / 3
        else:
            raise RuntimeError("The size is too long to initialize BFF")

        for label in temp_dict.keys():
            (h1, h2, h3) = self.__hashfunc__(label)
            temp_hash.setdefault(label, (h1, h2, h3))
            for h in (h1, h2, h3):
                temp_p2lable.setdefault(h, [])
                temp_p2lable[h].append(label)
            # temp_p2lable.setdefault(h1, [])
            # temp_p2lable[h1].append(label)
        can_pos = sorted(temp_p2lable.keys())

        label_stack = LifoQueue()
        while can_pos != []:
            # print(list(label_stack.queue))
            prev_len = len(can_pos)
            for pos in can_pos:
                lab_list = temp_p2lable.get(pos)
                if len(lab_list) == 0:
                    can_pos.remove(pos)
                elif len(lab_list) == 1:
                    label = lab_list[0]
                    label_stack.put(label)
                    can_pos.remove(pos)
                    for p in temp_hash.get(label):
                        temp_p2lable.get(p).remove(label)
                else:
                    continue
            post_len = len(can_pos)
            if prev_len == post_len:
                raise RuntimeError("Fail to initialize BFF")

        fuse_filter = [0 for i in range(self.N)]

        for i in range(label_stack.qsize()):
            label = label_stack.get()
            (p1, p2, p3) = temp_hash.get(label)
            print((p1, p2, p3))
            value = temp_dict.get(label)
            assert len(value) == 128

            # flag = sum([fuse_filter[x] for x in (p1, p2, p3)])
            # flag = len([p for p in (p1, p2, p3) if fuse_filter[p] == 0])
            single_pos = [p for p in (p1, p2, p3) if fuse_filter[p] == 0]
            # dummy_value = []
            xor_value = value
            for i in range(len(single_pos) - 1):
                # dummy_value.append(gen_key(1024))
                fuse_filter[single_pos.pop(i)] = gen_key(1024)
            for p in (p1, p2, p3):
                if p not in single_pos:
                    xor_value = bxor(xor_value, fuse_filter[p])
            assert len(single_pos) == 1
            fuse_filter[single_pos[0]] = xor_value

        print(fuse_filter)
        print(temp_hash)

        # verify correctness
        test_label = "N_NAMESELECT"
        (h1, h2, h3) = self.__hashfunc__(test_label)
        print(h1, h2, h3)
        rt = bxor(bxor(fuse_filter[h1], fuse_filter[h2]), fuse_filter[h3])
        vt = temp_dict.get(test_label)
        print(rt)
        print(vt)
        print(rt == vt)

    def calculate(self, poslist):
        pass


if __name__ == '__main__':
    a = hash_to_fixsize(1, b"cvcva3" + b"1")
    print(int.from_bytes(a, byteorder="big"))
