#!/usr/bin/python3

import os
import math
import hashlib
import hmac
import json
import pandas as pd
# import time
from .TDAG import TDAG
from charm.toolbox.symcrypto import SymmetricCryptoAbstraction
from charm.core.math.integer import randomBits
from queue import LifoQueue

DB_STRUCTION = {
    "customer": {
        "attributes":
            ['_id', 'C_NAME', 'C_ADDRESS', 'C_NATIONKEY', 'C_PHONE',
             'C_ACCTBAL', 'MKT_SEGMENT'],
        "type": [1, 1, 1, 1, 1, 1, 1]
    },
    "customer_rg": {
        "attributes":
            ['_id', 'C_NAME', 'C_ADDRESS', 'C_NATIONKEY', 'C_PHONE',
             'C_ACCTBAL', 'MKT_SEGMENT'],
        "type": [2, 1, 1, 1, 1, 1, 1]
    },
    "lineitem": {
        "attributes":
            ['L_ORDERKEY', 'L_PARTKEY', 'L_SUPPKEY', 'L_LINENUMBER',
             'L_QUANTITY', 'L_EXTENDEDPRICE', 'L_DISCOUNT', 'L_TAX',
             'L_RETURNFLAG', 'L_LINESTATUS', 'L_SHIPDATE', 'L_COMMITDATE',
             'L_RECEIPTDATE', 'L_SHIPINSTRUCT', 'L_SHIPMODE'],
        "type": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1]
    },
    "lineitem_rg": {
        "attributes":
            ['L_ORDERKEY', 'L_PARTKEY', 'L_SUPPKEY', 'L_LINENUMBER',
             'L_QUANTITY', 'L_EXTENDEDPRICE', 'L_DISCOUNT', 'L_TAX',
             'L_RETURNFLAG', 'L_LINESTATUS', 'L_SHIPDATE', 'L_COMMITDATE',
             'L_RECEIPTDATE', 'L_SHIPINSTRUCT', 'L_SHIPMODE'],
        "type": [2, 2, 2, 2, 2, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1]
    },
    "nation": {
        "attributes": ['_id', 'N_NAME', 'N_REGIONKEY'],
        "type": [1, 1, 1]
    },
    "orders": {
        "attributes":
            ['_id', 'O_CUSTKEY', 'O_ORDERSTATUS', 'O_TOTALPRICE',
             'O_ORDERDATE', 'O_ORDERPRIORITY', 'O_CLERK', 'O_SHIPPRIORITY'],
        "type": [1, 1, 1, 1, 1, 1, 1, 1]
    },
    "part": {
        "attributes": ['_id', 'P_NAME', 'P_MFGR', 'P_BRAND', 'P_TYPE',
                       'P_SIZE', 'P_CONTAINER', 'P_RETAILPRICE'],
        "type": [1, 1, 1, 1, 1, 1, 1, 1]

    },
    "partsupp": {
        "attributes": ['PS_PARTKEY', 'PS_SUPPKEY', 'PS_AVAILQTY',
                       'PS_SUPPLYCOST'],
        "type": [1, 1, 1, 1]
    },
    "region": {
        "attributes": ['_id', 'R_NAME'],
        "type": [1, 1]
    },
    "supplier": {
        "attributes": ['_id', 'S_NAME', 'S_ADDRESS', 'S_NATIONKEY',
                       'S_PHONE', 'S_ACCTBAL'],
        "type": [1, 1, 1, 1, 1, 1]
    }
}


def ParseRawData(folder_name, table_name):
    file_path = os.path.join(folder_name, table_name + ".tbl")
    raw_data = pd.read_csv(file_path, sep="|", header=None)
    # raw_data = raw_data.drop(columns=raw_data.columns[-1])
    raw_data = raw_data.drop(columns=raw_data.columns[-2:])
    raw_data.columns = DB_STRUCTION[table_name]["attributes"]
    attr_type = DB_STRUCTION[table_name]["type"]
    if "_id" not in raw_data.columns:
        raw_data["_id"] = range(len(raw_data.index))
        attr_type.append(1)
    return (table_name, raw_data, attr_type)


def gen_key(key_length):
    # key_length means bits
    assert key_length % 8 == 0
    temp_key = randomBits(key_length)
    return temp_key.to_bytes(int(key_length / 8), byteorder="big")


def prf_256(key, data):
    if not isinstance(data, bytes):
        data = bytes(data, "utf-8")
    h = hmac.new(key, data, hashlib.sha256)
    return h.digest()  # output's length is 32 bytes, i.e., 32 * 8 = 256


def aes_enc(key, plaintext):
    symcrypt = SymmetricCryptoAbstraction(key)
    cryptext = symcrypt.encrypt(plaintext)
    ct_dict = json.loads(cryptext)
    ct_dict.pop("ALG")  # Remove unnecessary field
    ct_dict.pop("MODE")  # Remove unnecessary field
    cryptext = json.dumps(ct_dict)
    return cryptext


def aes_dec(key, cryptext):
    if not isinstance(cryptext, str):
        cryptext = cryptext.decode("utf-8")
    cryptext = cryptext.strip("0")
    ct_dict = json.loads(cryptext)
    symcrypt = SymmetricCryptoAbstraction(key)
    format_cryptext = {
        "ALG": 0,
        "MODE": 2,
        "IV": ct_dict["IV"],
        "CipherText": ct_dict["CipherText"]
    }
    plaintext = symcrypt.decrypt(json.dumps(format_cryptext))
    return plaintext


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
    Use 3 hash functions map a lable to 3 consecutive segments.
    So it is faster than XOR Filter to find a singleton.
    """

    def __init__(self, hash_num=4, segment_range=16):
        # Set default number of hash functions as 3 (i.e., 3-wise)
        self.hash_num = hash_num
        self.segment_range = segment_range
        # self.segment_num = segment_num

    def __hashfunc__(self, key, segment_num):
        pos_list = []
        segment_pos = int.from_bytes(hash_to_fixsize(1, key),
                                     byteorder="big")
        segment_pos = segment_pos % segment_num

        for i in range(self.hash_num):
            pos = hash_to_fixsize(1, key + str(i))
            pos_int = int.from_bytes(pos, byteorder="big")
            pos_1 = int(pos_int % self.segment_range)
            pos_2 = int((segment_pos + i) % segment_num)
            pos_convert = pos_2 * self.segment_range + pos_1
            # + i * segment_range
            # pos_convert = pos_int % (self.hash_num * segment_range)
            pos_list.append(int(pos_convert))
        # print(pos_list)
        return pos_list

    def construct(self, dict_data, K_1, K_2, K_J,
                  att_list, type_list, Node_Index):
        temp_dict = {}
        temp_hash = {}
        temp_p2lable = {}
        for i, att in enumerate(att_list):
            # All attributes need to append "SELECT"

            # att + "SELECT" => enc(K_1, dict_data[att])
            label = att + "SELECT"
            # label = str(prf_256(K_2, label))
            value = bytes(aes_enc(K_1, str(dict_data[att])), "utf-8")
            # assert len(value) == 97
            if len(value) > 128:
                print(dict_data[att])
                raise RuntimeError(f"Ciphertext is too long ({len(value)} B).")
            # Padding to 128 Bytes with zeros
            value = value.ljust(128, b"0")
            temp_dict.setdefault(label, value)

            if type_list[i] >= 1:
                # All attributes need to append "WHERE" except for type 0

                # att + "WHERE" => PRF(K_2, dict_data[att])
                label = att + "WHERE"
                # label = str(prf_256(K_2, label))
                value = prf_256(K_2, str(dict_data[att]))
                assert len(value) == 32
                # Padding to 128 Bytes with zeros
                value = value.ljust(128, b"0")
                temp_dict.setdefault(label, value)

            if type_list[i] == 2:
                pass
                """
                node_dict, max_value = Node_Index.get(att)
                tdag = TDAG(max_value)
                node_set = tdag.__CollectParents__(dict_data[att], node_dict)
                for n in list(node_set):
                    label = att + "node" + n
                    label = str(prf_256(K_2, label))
                    value = prf_256(K_2, n)
                    value = value.ljust(128, b"0")
                    temp_dict.setdefault(label, value)
                """

            if type_list[i] == 3:
                # For type 3, it also need to append "JOIN"

                # att + "JOIN" => PRF(K_J, dict_data[att])
                label = att + "JOIN"
                value = prf_256(K_J, str(dict_data[att]))
                assert len(value) == 32
                # Padding to 128 Bytes with zeros
                value = value.ljust(128, b"0")
                temp_dict.setdefault(label, value)

        # Set an appropriate size of BFF.
        # Default number of segments is 3.
        # The length of each segment is power of 2.
        # So the choices of segment's length is [4, 8, 16]
        label_num = len(temp_dict.keys())
        segment_num = math.ceil(1.2 * label_num / self.segment_range)
        # print(f"-----------{segment_num}")
        # segment_range = math.ceil(1.1 * label_num / self.segment_num)
        # segment_range = math.ceil(1.5 * label_num / self.hash_num)
        # if segment_range <= 4:
            # segment_range = 4
        # if segment_range <= 8:
            # segment_range = 8
        # elif segment_range <= 16:
            # segment_range = 16
        # elif segment_range <= 24:
            # segment_range = 24
        # else:
            # raise RuntimeError(f"The size {label_num} is too long to initialize BFF")
        # N = segment_range * self.hash_num  # N is the length of the filter
        # N = self.segment_range * segment_num
        N = self.segment_range * segment_num
        # print(N)

        for label in temp_dict.keys():
            hash_tuple = self.__hashfunc__(label, segment_num)
            # hash_tuple = self.__hashfunc__(label, segment_range)
            temp_hash.setdefault(label, hash_tuple)
            for h in hash_tuple:
                temp_p2lable.setdefault(h, [])
                temp_p2lable[h].append(label)
        can_pos = sorted(temp_p2lable.keys())

        label_stack = LifoQueue()
        while can_pos != []:
            prev_len = len(can_pos)
            # print(prev_len)
            for pos in can_pos:
                lab_list = temp_p2lable.get(pos)
                if len(lab_list) == 0:
                    can_pos.remove(pos)
                elif len(lab_list) == 1:
                    label = lab_list[0]
                    label_stack.put(label)  # Add a singleton to a stack
                    can_pos.remove(pos)
                    for p in temp_hash.get(label):
                        temp_p2lable.get(p).remove(label)
                else:
                    continue
            post_len = len(can_pos)
            if prev_len == post_len:
                print(label_num)
                # print(segment_range * self.hash_num)
                print(N)
                print(temp_dict.keys())
                print(dict_data.get("_id"))
                # print(can_pos)
                # print([temp_p2lable.get(x) for x in can_pos])
                # print(temp_p2lable.get(can_pos[0]))
                # x = [temp_p2lable.get(x) for x in can_pos]
                # y = []
                # for i in x:
                    # y.extend(i)
                # print(set(y))
                # error_pos = temp_p2lable.get(can_pos[0])
                # print(self.__hashfunc__(error_pos[0], segment_range))
                # print(self.__hashfunc__(error_pos[1], segment_range))

                raise RuntimeError("Fail to initialize BFF")

        fuse_filter = [0 for i in range(N)]  # Initialize a binary fuse filter

        for i in range(label_stack.qsize()):
            label = label_stack.get()
            pos_tuple = temp_hash.get(label)
            value = temp_dict.get(label)
            assert len(value) == 128

            single_pos = [p for p in pos_tuple if fuse_filter[p] == 0]
            xor_value = value
            for i in range(len(single_pos) - 1):
                fuse_filter[single_pos.pop(0)] = gen_key(1024)
            for p in pos_tuple:
                if p not in single_pos:
                    xor_value = bxor(xor_value, fuse_filter[p])
            assert len(single_pos) == 1
            fuse_filter[single_pos[0]] = xor_value
        # print("Done!")
        return fuse_filter

        # verify correctness
        # test_label = "L_SUPPKEYSELECT"
        # (h1, h2, h3) = self.__hashfunc__(test_label)
        # rt = bxor(bxor(fuse_filter[h1], fuse_filter[h2]), fuse_filter[h3])
        # vt = temp_dict.get(test_label)
        # print(aes_dec(K_1, rt))
        # print(aes_dec(K_1, vt))
        # print(rt == vt)

    def calculate(self, poslist):
        pass


if __name__ == '__main__':
    a = hash_to_fixsize(1, b"cvcva3" + b"1")
    print(int.from_bytes(a, byteorder="big"))
