#!/usr/bin/python3
import os
# import pickle
import pandas as pd
from tools import gen_key, prf_256, BFF


DB_STRUCTION = {
    "customer": {
        "attributes":
            ['_id', 'C_NAME', 'C_ADDRESS', 'C_NATIONKEY', 'C_PHONE',
             'C_ACCTBAL', 'MKT_SEGMENT']
    },
    "lineitem": {
        "attributes":
            ['L_ORDERKEY', 'L_PARTKEY', 'L_SUPPKEY', 'L_LINENUMBER',
             'L_QUANTITY', 'L_EXTENDEDPRICE', 'L_DISCOUNT', 'L_TAX',
             'L_RETURNFLAG', 'L_LINESTATUS', 'L_SHIPDATE', 'L_COMMITDATE',
             'L_RECEIPTDATE', 'L_SHIPINSTRUCT', 'L_SHIPMODE']
    },
    "nation": {
        "attributes": ['_id', 'N_NAME', 'N_REGIONKEY'],
        "type": ['1', '1', '1']
    },
    "orders": {
        "attributes":
            ['_id', 'O_CUSTKEY', 'O_ORDERSTATUS', 'O_TOTALPRICE',
             'O_ORDERDATE', 'O_ORDERPRIORITY', 'O_CLERK', 'O_SHIPPRIORITY']
    },
    "part": {
        "attributes": ['_id', 'P_NAME', 'P_MFGR', 'P_BRAND', 'P_TYPE',
                       'P_SIZE', 'P_CONTAINER', 'P_RETAILPRICE']
    },
    "partsupp": {
        "attributes": ['PS_PARTKEY', 'PS_SUPPKEY', 'PS_AVAILQTY',
                       'PS_SUPPLYCOST']
    },
    "region": {
        "attributes": ['_id', 'R_NAME']
    },
    "supplier": {
        "attributes": ['_id', 'S_NAME', 'S_ADDRESS', 'S_NATIONKEY',
                       'S_PHONE', 'S_ACCTBAL']
    }
}


class DB(object):
    """docstring for DB"""

    def __init__(self, folder_name, table_name):
        # attr_list = DB_STRUCTION[table_name]
        file_path = os.path.join(folder_name, table_name + ".tbl")
        raw_data = pd.read_csv(file_path, sep="|", header=None)
        raw_data = raw_data.drop(columns=raw_data.columns[-2:])
        raw_data.columns = DB_STRUCTION[table_name]["attributes"]
        self.invert_index = {}
        self.raw_data = raw_data
        self.table_name = table_name

    def constructIndex(self, K_T, K_e):
        K_2 = prf_256(K_T, self.table_name)
        # print(self.raw_data)
        for row in self.raw_data.iterrows():
            row_dict = row[1].to_dict()
            print(row_dict)
            for attr in self.raw_data.columns:
                if attr == "_id":
                    label = self.table_name + attr + str(row_dict[attr])
                    label = prf_256(K_T, label)
                    value = row_dict
                    K_1 = prf_256(K_e, label)
                    # here, value is encoded by BFF,
                    # such as value = BFF(row_dict)
                    bff = BFF()
                    bff.construct(row_dict, K_1, K_2, self.raw_data.columns,
                                  DB_STRUCTION[self.table_name]["type"])
                    break
                else:
                    label = attr + str(row_dict[attr])
                    label = prf_256(K_T, label)
                    value = self.table_name + "_id" + str(row_dict["_id"])
                self.invert_index.setdefault(label, [])
                self.invert_index[label].append(value)
            break


if __name__ == '__main__':
    K_T = gen_key(256)
    K_e = gen_key(256)
    # print(K_T)
    print(len(K_T))

    test_db = DB("../data/sf0.01/", "nation")
    test_db.constructIndex(K_T, K_e)
    # print(test_db.invert_index)

    """ Query Test
    query_label = prf_256(K_T, "N_REGIONKEY" + "1")
    print(test_db.invert_index.get(query_label))
    """
