#!/usr/bin/python3
from collections import namedtuple
from utils.tools import gen_key, ParseRawData

SecretKey = namedtuple("SecretKey", ["K_1", "K_R", "K_V", "K_C", "K_D", "K_c"])


class Client(object):
    """docstring for Client"""

    def __init__(self, lamba=256):
        # (K_1, K_R, K_V, K_C, K_D)
        self.SK = SecretKey(*[gen_key(lamba) for i in range(5)], [])

    def load_tables(self, folder_name, table_name_list):
        Raw_Tables = []
        for table_name in table_name_list:
            Raw_Tables.append(ParseRawData(folder_name, table_name))
        self.Raw_Tables = Raw_Tables

    def construct_index(self):
        # (EMM_R, EMM_C, EMM_V, EDX)
        MM_R = {}
        MM_C = {}
        MM_V = {}
        EDX = {}
        print(self.Raw_Tables)
        # for series in self.Raw_Tables.items():
            # print(series)
        for table_info in self.Raw_Tables:
            (t_name, t_data, t_type) = table_info
            for attr, column in t_data.items():
                label_c = t_name + attr
                MM_C.setdefault(label_c, list(column))
            for row in t_data.iterrows():
                row_dict = row[1].to_dict()
                value_r = []
                for attr in t_data.columns:
                    value_str = str(row_dict[attr])
                    value_r.append(value_str)
                    if attr == "_id":
                        label_r = t_name + attr + value_str
                    else:
                        label_v = attr + value_str
                        value_v = t_name + "_id" + str(row_dict["_id"])
                        MM_V.setdefault(label_v, [])
                        MM_V[label_v].append(value_v)
                MM_R.setdefault(label_r, value_r)
        self.MM_R = MM_R
        self.MM_V = MM_V
        self.MM_C = MM_C


if __name__ == '__main__':
    ct = Client()
    tb_list = ["customer"]
    ct.load_tables("../data/sf0.001", tb_list)
    ct.construct_index()
    # print(ct.MM_R)
    print(ct.MM_C)
