#!/usr/bin/python3
import os
import pickle
import pandas as pd
from utils.tools import gen_key, prf_256, BFF


DB_STRUCTION = {
    "customer": {
        "attributes":
            ['_id', 'C_NAME', 'C_ADDRESS', 'C_NATIONKEY', 'C_PHONE',
             'C_ACCTBAL', 'MKT_SEGMENT'],
        "type": [1, 1, 1, 1, 1, 1, 1]
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


class Client(object):
    """docstring for Client"""

    def __init__(self, lamba=256):
        (K_T, K_e, K_J) = [gen_key(lamba) for i in range(3)]
