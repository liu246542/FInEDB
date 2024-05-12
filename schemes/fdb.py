#!/usr/bin/python3
import os
import pickle
import pandas as pd
from collections import namedtuple
from utils.tools import gen_key, prf_256, BFF, ParseRawData


SecretKey = namedtuple("SecretKey", ["K_T", "K_S", "K_J"])


class Client(object):
    """docstring for Client"""

    def __init__(self, lamba=256):
        # (K_T, K_e, K_J) = [gen_key(lamba) for i in range(3)]
        self.SK = SecretKey(*[gen_key(lamba) for i in range(3)])

    def load_tables(self, folder_name, table_name_list):
        Raw_Tables = []
        for table_name in table_name_list:
            Raw_Tables.append(ParseRawData(folder_name, table_name))
        print("-" * 20 + "LOAD COMPLETE" + "-" * 20)
        self.Raw_Tables = Raw_Tables

    def __index2emm__(self, inverted_index):
        pass

    def construct_index(self):
        # Raw_Tables => inverted index
        inverted_index = {}
        bff = BFF()
        K_J = self.SK.K_J
        for table_info in self.Raw_Tables:
            (t_name, t_data, t_type) = table_info
            K_e = prf_256(self.SK.K_S, t_name)  # K_1
            K_v = prf_256(self.SK.K_T, t_name)  # K_2
            # K_2 = prf_256(self.SK.K_T, t_name)
            for row in t_data.iterrows():
                # print("|")
                # print(f"Row content: \n {row}")
                row_dict = row[1].to_dict()
                for attr in t_data.columns:
                    if attr == "_id":
                        label = t_name + attr + str(row_dict[attr])
                        label = prf_256(self.SK.K_T, label)
                        value = bff.construct(row_dict, K_e, K_v, K_J,
                                              t_data.columns, t_type)
                    else:
                        label = attr + str(row_dict[attr])
                        label = prf_256(self.SK.K_T, label)
                        value = t_name + "_id" + str(row_dict["_id"])
                    inverted_index.setdefault(label, [])
                    inverted_index[label].append(value)
                # print("-" * 40)
        remm = self.__index2emm__(inverted_index)


if __name__ == '__main__':
    ct = Client()
    # print(ct.SK.K_T)
    tb_list = ["customer", "lineitem", "nation", "orders",
               "part", "partsupp", "region", "supplier"]
    ct.load_tables("../data/sf0.01", tb_list)
    ct.construct_index()
