#!/usr/bin/python3

import os
import math
import hmac
import json
import hashlib
import pandas as pd
from .TDAG import TDAG
from collections import namedtuple
from charm.toolbox.symcrypto import SymmetricCryptoAbstraction
from charm.core.math.integer import randomBits
from queue import LifoQueue

DB_STRUCTION = {
    "customer": {
        "attributes":
            ['_id', 'C_NAME', 'C_ADDRESS', 'C_NATIONKEY', 'C_PHONE',
             'C_ACCTBAL', 'MKT_SEGMENT', 'C_COMMENT'],
        "type": [1, 1, 1, 1, 1, 1, 1, 0]
    },
    "customer_rg": {
        "attributes":
            ['_id', 'C_NAME', 'C_ADDRESS', 'C_NATIONKEY', 'C_PHONE',
             'C_ACCTBAL', 'MKT_SEGMENT', 'C_COMMENT'],
        "type": [2, 1, 1, 1, 1, 1, 1, 0]
    },
    "customer_join": {
        "attributes":
            ['_id', 'C_NAME', 'C_ADDRESS', 'C_NATIONKEY', 'C_PHONE',
             'C_ACCTBAL', 'MKT_SEGMENT', 'C_COMMENT'],
        "type": [3, 1, 1, 3, 1, 1, 1, 0]
    },
    "lineitem": {
        "attributes":
            ['L_ORDERKEY', 'L_PARTKEY', 'L_SUPPKEY', 'L_LINENUMBER',
             'L_QUANTITY', 'L_EXTENDEDPRICE', 'L_DISCOUNT', 'L_TAX',
             'L_RETURNFLAG', 'L_LINESTATUS', 'L_SHIPDATE', 'L_COMMITDATE',
             'L_RECEIPTDATE', 'L_SHIPINSTRUCT', 'L_SHIPMODE', 'L_COMMENT'],
        "type": [1, 1, 1, 1, 1, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 0]
    },
    "lineitem_rg": {
        "attributes":
            ['L_ORDERKEY', 'L_PARTKEY', 'L_SUPPKEY', 'L_LINENUMBER',
             'L_QUANTITY', 'L_EXTENDEDPRICE', 'L_DISCOUNT', 'L_TAX',
             'L_RETURNFLAG', 'L_LINESTATUS', 'L_SHIPDATE', 'L_COMMITDATE',
             'L_RECEIPTDATE', 'L_SHIPINSTRUCT', 'L_SHIPMODE', 'L_COMMENT'],
        "type": [2, 2, 2, 2, 2, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 0]
    },
    "lineitem_join": {
        "attributes":
            ['L_ORDERKEY', 'L_PARTKEY', 'L_SUPPKEY', 'L_LINENUMBER',
             'L_QUANTITY', 'L_EXTENDEDPRICE', 'L_DISCOUNT', 'L_TAX',
             'L_RETURNFLAG', 'L_LINESTATUS', 'L_SHIPDATE', 'L_COMMITDATE',
             'L_RECEIPTDATE', 'L_SHIPINSTRUCT', 'L_SHIPMODE', 'L_COMMENT'],
        "type": [3, 3, 3, 1, 1, 1, 1, 1, 1, 1,
                 1, 1, 1, 1, 1, 0]
    },
    "nation": {
        "attributes": ['_id', 'N_NAME', 'N_REGIONKEY', 'N_COMMENT'],
        "type": [1, 1, 1, 0]
    },
    "nation_rg": {
        "attributes": ['_id', 'N_NAME', 'N_REGIONKEY', 'N_COMMENT'],
        "type": [2, 1, 2, 0]
    },
    "nation_join": {
        "attributes": ['_id', 'N_NAME', 'N_REGIONKEY', 'N_COMMENT'],
        "type": [3, 1, 3, 0]
    },
    "orders": {
        "attributes":
            ['_id', 'O_CUSTKEY', 'O_ORDERSTATUS', 'O_TOTALPRICE',
             'O_ORDERDATE', 'O_ORDERPRIORITY', 'O_CLERK', 'O_SHIPPRIORITY',
             'O_COMMENT'],
        "type": [1, 1, 1, 1, 1, 1, 1, 1, 0]
    },
    "orders_rg": {
        "attributes":
            ['_id', 'O_CUSTKEY', 'O_ORDERSTATUS', 'O_TOTALPRICE',
             'O_ORDERDATE', 'O_ORDERPRIORITY', 'O_CLERK', 'O_SHIPPRIORITY',
             'O_COMMENT'],
        "type": [2, 2, 1, 1, 1, 1, 1, 1, 0]
    },
    "orders_join": {
        "attributes":
            ['_id', 'O_CUSTKEY', 'O_ORDERSTATUS', 'O_TOTALPRICE',
             'O_ORDERDATE', 'O_ORDERPRIORITY', 'O_CLERK', 'O_SHIPPRIORITY',
             'O_COMMENT'],
        "type": [3, 3, 1, 1, 1, 1, 1, 1, 0]
    },
    "part": {
        "attributes": ['_id', 'P_NAME', 'P_MFGR', 'P_BRAND', 'P_TYPE',
                       'P_SIZE', 'P_CONTAINER', 'P_RETAILPRICE', 'P_COMMENT'],
        "type": [1, 1, 1, 1, 1, 1, 1, 1, 0]

    },
    "part_rg": {
        "attributes": ['_id', 'P_NAME', 'P_MFGR', 'P_BRAND', 'P_TYPE',
                       'P_SIZE', 'P_CONTAINER', 'P_RETAILPRICE', 'P_COMMENT'],
        "type": [2, 1, 1, 1, 1, 2, 1, 1, 0]

    },
    "part_join": {
        "attributes": ['_id', 'P_NAME', 'P_MFGR', 'P_BRAND', 'P_TYPE',
                       'P_SIZE', 'P_CONTAINER', 'P_RETAILPRICE', 'P_COMMENT'],
        "type": [3, 1, 1, 1, 1, 1, 1, 1, 0]

    },
    "partsupp": {
        "attributes": ['PS_PARTKEY', 'PS_SUPPKEY', 'PS_AVAILQTY',
                       'PS_SUPPLYCOST', 'PS_COMMENT'],
        "type": [1, 1, 1, 1, 0]
    },
    "partsupp_rg": {
        "attributes": ['PS_PARTKEY', 'PS_SUPPKEY', 'PS_AVAILQTY',
                       'PS_SUPPLYCOST', 'PS_COMMENT'],
        "type": [2, 2, 2, 1, 0]
    },
    "partsupp_join": {
        "attributes": ['PS_PARTKEY', 'PS_SUPPKEY', 'PS_AVAILQTY',
                       'PS_SUPPLYCOST', 'PS_COMMENT'],
        "type": [3, 3, 1, 1, 0]
    },
    "region": {
        "attributes": ['_id', 'R_NAME', 'R_COMMENT'],
        "type": [1, 1, 0]
    },
    "region_rg": {
        "attributes": ['_id', 'R_NAME', 'R_COMMENT'],
        "type": [2, 1, 0]
    },
    "region_join": {
        "attributes": ['_id', 'R_NAME', 'R_COMMENT'],
        "type": [3, 1, 0]
    },
    "supplier": {
        "attributes": ['_id', 'S_NAME', 'S_ADDRESS', 'S_NATIONKEY',
                       'S_PHONE', 'S_ACCTBAL', 'S_COMMENT'],
        "type": [1, 1, 1, 1, 1, 1, 0]
    },
    "supplier_rg": {
        "attributes": ['_id', 'S_NAME', 'S_ADDRESS', 'S_NATIONKEY',
                       'S_PHONE', 'S_ACCTBAL', 'S_COMMENT'],
        "type": [2, 1, 1, 2, 1, 1, 0]
    },
    "supplier_join": {
        "attributes": ['_id', 'S_NAME', 'S_ADDRESS', 'S_NATIONKEY',
                       'S_PHONE', 'S_ACCTBAL', 'S_COMMENT'],
        "type": [3, 1, 1, 3, 1, 1, 0]
    }
}

BFF_INFO = namedtuple("BFF_INFO", ["nonce", "number", "length", "totalnum"])


def ParseRawData(folder_name, table_name, comment_flag=0):
    file_path = os.path.join(folder_name, table_name.split("_")[0] + ".tbl")
    raw_data = pd.read_csv(file_path, sep="|", header=None)
    if comment_flag:
        raw_data = raw_data.drop(columns=raw_data.columns[-1])
        raw_data.columns = DB_STRUCTION[table_name]["attributes"]
        attr_type = DB_STRUCTION[table_name]["type"]
    else:
        raw_data = raw_data.drop(columns=raw_data.columns[-2:])
        raw_data.columns = DB_STRUCTION[table_name]["attributes"][0:-1]
        attr_type = DB_STRUCTION[table_name]["type"][0:-1]

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


def prf_any(key, data, output_length):
    if not isinstance(data, bytes):
        data = bytes(data, "utf-8")
    h = hashlib.blake2b(key=key, digest_size=output_length)
    h.update(data)
    return h.digest()


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
    if b2 == 0:
        return b1
    assert len(b1) == len(b2)
    return bytes(x ^ y for x, y in zip(b1, b2))


def bxor2(b1, b2):
    if b1 == 0:
        return b2
    if b2 == 0:
        return b1
    assert len(b1) == len(b2)
    return b1 ^ b2


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

    def __init__(self, hash_num=3, nonce=None):
        # Set default number of hash functions as 3 (i.e., 3-wise)
        self.hash_num = hash_num
        # if nonce is None:
            # self.nonce = str(gen_key(8))
        # else:
            # self.nonce = nonce
        self.nonce = str(gen_key(8))

    def __hashfunc__(self, key, segment_num, segment_range):
        pos_list = []
        segment_pos = int.from_bytes(hash_to_fixsize(1, key),
                                     byteorder="big")
        segment_pos = segment_pos % (segment_num - self.hash_num + 1)

        for i in range(self.hash_num):
            pos = hash_to_fixsize(1, key + self.nonce + str(i))
            pos_int = int.from_bytes(pos, byteorder="big")
            pos_1 = int(pos_int % segment_range)
            pos_2 = int((segment_pos + i) % segment_num)
            pos_convert = pos_2 * segment_range + pos_1
            pos_list.append(int(pos_convert))
        return pos_list

    def construct(self, dict_data, K_1, K_2, K_J,
                  K_T, att_list, type_list, Node_Index):
        temp_dict = {}
        temp_hash = {}
        temp_p2lable = {}
        temp_inverted_index = {}

        for i, att in enumerate(att_list):
            # All attributes need to append "SELECT"

            label_prime = gen_key(32)  # 4 bytes
            value_prime = bytes(aes_enc(K_1, str(dict_data[att])), "utf-8")
            temp_inverted_index.setdefault(label_prime, [value_prime])

            # att + "SELECT" => enc(K_1, dict_data[att])
            label = att + "SELECT"
            # label = str(prf_256(K_2, label))
            # value = label_prime
            value = prf_any(K_T, label_prime, 4)

            assert len(value) == 4
            temp_dict.setdefault(label, value)

            if type_list[i] >= 1:
                # All attributes need to append "WHERE" except for type 0

                # att + "WHERE" => PRF(K_2, dict_data[att])
                label = att + "WHERE"
                # label = str(prf_256(K_2, label))
                value = prf_any(K_2, str(dict_data[att]), 4)
                assert len(value) == 4
                temp_dict.setdefault(label, value)

            if type_list[i] == 2:
                node_dict, max_value = Node_Index.get(att)
                tdag = TDAG(max_value)
                node_set = tdag.__CollectParents__(dict_data[att], node_dict)
                for n in list(node_set):
                    label = n + att + "node"
                    # label = str(prf_256(K_2, label))
                    # value = prf_256(K_2, n)
                    value = prf_any(K_2, n, 4)
                    assert len(value) == 4
                    temp_dict.setdefault(label, value)

            if type_list[i] == 3:
                # For type 3, it also need to append "JOIN"

                # att + "JOIN" => PRF(K_J, dict_data[att])
                label = att + "JOIN"
                # value = prf_256(K_J, str(dict_data[att]))
                value = prf_any(K_J, str(dict_data[att]), 4)
                assert len(value) == 4
                temp_dict.setdefault(label, value)

        # Set an appropriate size of BFF.
        # Default number of segments is 3.
        label_num = len(temp_dict.keys())
        segment_range = math.ceil(4.8 * (label_num ** 0.58))
        segment_num = math.ceil(1.125 * label_num / segment_range)
        # segment_num = math.ceil(1.5 * label_num / segment_range)
        if segment_num < self.hash_num:
            segment_num = self.hash_num
            segment_range = math.ceil(1.5 * label_num / segment_num)

        N = segment_range * segment_num  # N is the length of the filter

        self.bff_info = BFF_INFO(self.nonce, segment_num,
                                 segment_range, label_num)

        for label in temp_dict.keys():
            hash_tuple = self.__hashfunc__(label, segment_num, segment_range)
            temp_hash.setdefault(label, hash_tuple)
            for h in hash_tuple:
                temp_p2lable.setdefault(h, [])
                temp_p2lable[h].append(label)
        can_pos = sorted(temp_p2lable.keys())

        label_stack = LifoQueue()
        while can_pos != []:
            prev_len = len(can_pos)
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
                # ----------------DEBUG----------------
                # print(f"segment range is {segment_range}")
                # print(f"segment number is {segment_num}")
                # print(f"total element num is {label_num}")
                # print(can_pos)
                # print([len(temp_p2lable.get(x)) for x in can_pos])
                # ----------------DEBUG----------------
                return (0, [], {}, ())

        fuse_filter = [0 for i in range(N)]  # Initialize a binary fuse filter

        for i in range(label_stack.qsize()):
            label = label_stack.get()
            pos_tuple = temp_hash.get(label)
            value = temp_dict.get(label)
            assert len(value) == 4

            single_pos = [p for p in pos_tuple if fuse_filter[p] == 0]
            xor_value = value
            for i in range(len(single_pos) - 1):
                fuse_filter[single_pos.pop(0)] = gen_key(32)
            for p in pos_tuple:
                if p not in single_pos:
                    xor_value = bxor(xor_value, fuse_filter[p])
            assert len(single_pos) == 1
            fuse_filter[single_pos[0]] = xor_value
        return [1, fuse_filter, temp_inverted_index, self.bff_info]

    def resolve_position(self, query_label, segment_num, segment_range):
        # key, segment_num, segment_range):
        return self.__hashfunc__(query_label, segment_num, segment_range)

    def calculate(self, poslist):
        pass


if __name__ == '__main__':
    a = hash_to_fixsize(1, b"cvcva3" + b"1")
    print(int.from_bytes(a, byteorder="big"))
