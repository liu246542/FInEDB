#!/usr/bin/python3

import os
import pickle
import pandas as pd


def read_tbl(folder_name, tbl_name, attr_list):
    file_name = os.path.join(folder_name, tbl_name)
    data_record = pd.read_csv(file_name, sep="|", header=None)
    data_record = data_record.drop(columns=data_record.columns[-2:])
    data_record.columns = attr_list
    dict_data = [x[1].to_dict() for x in data_record.iterrows()]
    print(data_record)
    return dict_data


if __name__ == '__main__':
    DB_FOLDER = "./data/sf0.01/"

    DB_STRUCTION = [
        {
            "name": "customer",
            "attributes":
                ['_id', 'C_NAME', 'C_ADDRESS', 'C_NATIONKEY', 'C_PHONE',
                 'C_ACCTBAL', 'MKT_SEGMENT']
        },
        {
            "name": "lineitem",
            "attributes":
                ['L_ORDERKEY', 'L_PARTKEY', 'L_SUPPKEY', 'L_LINENUMBER',
                 'L_QUANTITY', 'L_EXTENDEDPRICE', 'L_DISCOUNT', 'L_TAX',
                 'L_RETURNFLAG', 'L_LINESTATUS', 'L_SHIPDATE', 'L_COMMITDATE',
                 'L_RECEIPTDATE', 'L_SHIPINSTRUCT', 'L_SHIPMODE']
        },
        {
            "name": "nation",
            "attributes": ['_id', 'N_NAME', 'N_REGIONKEY']
        },
        {
            "name": "orders",
            "attributes":
                ['_id', 'O_CUSTKEY', 'O_ORDERSTATUS', 'O_TOTALPRICE',
                 'O_ORDERDATE', 'O_ORDERPRIORITY', 'O_CLERK', 'O_SHIPPRIORITY']
        },
        {
            "name": "part",
            "attributes":
                ['_id', 'P_NAME', 'P_MFGR', 'P_BRAND', 'P_TYPE',
                 'P_SIZE', 'P_CONTAINER', 'P_RETAILPRICE']
        },
        {
            "name": "partsupp",
            "attributes": ['PS_PARTKEY', 'PS_SUPPKEY', 'PS_AVAILQTY',
                           'PS_SUPPLYCOST']
        },
        {
            "name": "region",
            "attributes": ['_id', 'R_NAME']
        },
        {
            "name": "supplier",
            "attributes": ['_id', 'S_NAME', 'S_ADDRESS', 'S_NATIONKEY',
                           'S_PHONE', 'S_ACCTBAL']
        }
    ]

    for s in DB_STRUCTION:
        data = read_tbl(DB_FOLDER, s["name"] + ".tbl", s["attributes"])
        with open(os.path.join(DB_FOLDER, s["name"]), "wb") as f:
            pickle.dump(data, f)
