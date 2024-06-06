#!/usr/bin/python3

from schemes import fdb
from pprint import pprint
from collections import namedtuple

SQL_Query = namedtuple("SQL_Query", ["Select", "Where", "Value"])

if __name__ == '__main__':
    test_folder = ["../data/sf0.001"]
    """
    tb_list = ["customer", "lineitem", "nation", "orders",
               "part", "partsupp", "region", "supplier"]
    """
    tb_list = ["customer"]

    ct_fdb = fdb.Client()
    ct_fdb.load_tables(test_folder[0], tb_list)
    emm = ct_fdb.construct_index()
    # print(len(pickle.dumps(emm, -1)))
    # print(ct_fdb.bff_dict)
    sv_fdb = fdb.Server(emm)

    select_att = ["_id"]
    where_att = ["C_NATIONKEY"]
    value_list = ["3"]
    query_tuple = SQL_Query(select_att, where_att, value_list)
    print("|")
    print("*" * 20 + "Query Tuple" + "*" * 20)
    pprint(query_tuple)
    print("|")

    tk = ct_fdb.gen_token(query_tuple, "customer")
    print("*" * 20 + "Query Tokens" + "*" * 20)
    pprint(tk)
    print("|")

    enc_res = sv_fdb.query(tk)
    print("*" * 20 + "Query Results" + "*" * 20)
    pprint(enc_res)
    print("|")

    pla_res = ct_fdb.decrypt_res(enc_res, "customer")
    print("*" * 20 + "Decrypted Results" + "*" * 20)
    pprint(pla_res)
    print("|")
