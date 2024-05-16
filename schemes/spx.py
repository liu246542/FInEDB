#!/usr/bin/python3

import pickle
from collections import namedtuple
from utils.tools import gen_key, ParseRawData, aes_enc
from utils.TSet import TSet
from utils import pysize, TDAG

SecretKey = namedtuple("SecretKey", ["K_1", "K_R", "K_V", "K_C", "K_D", "K_c"])


class Client(object):
    """docstring for Client"""

    def __init__(self, lamba=256, SK=None):
        # (K_1, K_R, K_V, K_C, K_D)
        if SK is None:
            self.SK = SecretKey(*[gen_key(lamba) for i in range(5)], [])
        else:
            self.SK = SK

    def load_tables(self, folder_name, table_name_list):
        Raw_Tables = []
        for table_name in table_name_list:
            Raw_Tables.append(ParseRawData(folder_name, table_name))
        print("-" * 20 + "LOAD COMPLETE" + "-" * 20)
        self.Raw_Tables = Raw_Tables

    def construct_index(self):
        # (EMM_R, EMM_C, EMM_V, EDX)
        MM_R = {}
        MM_C = {}
        MM_V = {}
        EDX = {}
        STE = TSet()
        for table_info in self.Raw_Tables:
            (t_name, t_data, t_type) = table_info
            for i, t in enumerate(t_type):
                if t == 2:
                    attr = t_data.columns[i]
                    value_list = list(t_data[attr])
                    row_list = list(t_data["_id"])
                    value_dict = {}
                    for i, v in enumerate(value_list):
                        value_dict.setdefault(v, [])
                        value_dict[v].append(row_list[i])

                    max_value = max(value_list)
                    tdag = TDAG.TDAG(max_value)
                    (MM_range, node_dict) = tdag.construct(value_list)

                    mm_tdag = {}

                    for node_name in MM_range.keys():
                        v_list = MM_range.get(node_name)

                        label = t_name + attr + node_name
                        value = []

                        for v in v_list:
                            rowid_list = value_dict.get(v)
                            for rowid in rowid_list:
                                value_v = t_name + "_id" + str(rowid)
                                rtk = STE.gen_token(value_v, self.SK.K_R)
                                value.append(rtk)
                        mm_tdag.setdefault(label, value)
                    MM_V.update(mm_tdag)
            # print(len(MM_V.keys()))
            # raise RuntimeError("Break")

            for attr, column in t_data.items():
                label_c = t_name + attr
                enc_column = [bytes(aes_enc(self.SK.K_1, str(x)), "utf-8")
                              for x in list(column)]
                # enc_value = aes_enc(self.SK.K_1, value_v)
                MM_C.setdefault(label_c, enc_column)
            for row in t_data.iterrows():
                row_dict = row[1].to_dict()
                value_r = []
                for attr in t_data.columns:
                    value_str = str(row_dict[attr])
                    enc_value = bytes(aes_enc(self.SK.K_1, value_str), "utf-8")
                    value_r.append(enc_value)
                    if attr == "_id":
                        label_r = t_name + attr + value_str
                    else:
                        label_v = attr + value_str
                        value_v = t_name + "_id" + str(row_dict["_id"])
                        rtk_r = STE.gen_token(value_v, self.SK.K_R)
                        MM_V.setdefault(label_v, [])
                        MM_V[label_v].append(rtk_r)
                MM_R.setdefault(label_r, value_r)
        # self.MM_R = MM_R
        # self.MM_V = MM_V
        # self.MM_C = MM_C
        EMM_R = STE.setup(MM_R, self.SK.K_R)
        EMM_C = STE.setup(MM_C, self.SK.K_C)
        EMM_V = STE.setup(MM_V, self.SK.K_V)
        return (EMM_R, EMM_C, EMM_V, EDX)
        # with open("./DUMPs/spx_r.pkl", "wb") as f:
            # pickle.dump((EMM_R, EMM_C, EMM_V), f)


if __name__ == '__main__':
    ct = Client()
    # tb_list = ["customer"]
    # tb_list = ["customer", "lineitem", "nation", "orders",
               # "part", "partsupp", "region", "supplier"]
    tb_list = ["lineitem"]
    ct.load_tables("../data/sf0.001", tb_list)
    ALL_EMM = ct.construct_index()
    # print(pysize.get_size(ALL_EMM))
    print(len(pickle.dumps(ALL_EMM, -1)))
    # print(ct.MM_R)
    # print(ct.MM_C)
    # print(ct.MM_V)
