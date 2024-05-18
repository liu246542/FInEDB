#!/usr/bin/python3

import pickle
import pandas as pd
from schemes import spx, fdb
from decimal import Decimal


def test_storage_size(folder_list, tb_list, rg_tb_list, join_tb_list):
    original_size_fdb = []
    addrange_size_fdb = []
    addjoin_size_fdb = []
    ratio_rg_fdb = []
    ratio_jo_fdb = []

    for folder_name in folder_list:
        ct_fdb = fdb.Client()
        ct_fdb.load_tables(folder_name, rg_tb_list)
        emm = ct_fdb.construct_index()
        addrange_size_fdb.append(len(pickle.dumps(emm, -1)))
        del emm

        ct_fdb.load_tables(folder_name, tb_list)
        emm = ct_fdb.construct_index()
        original_size_fdb.append(len(pickle.dumps(emm, -1)))
        del emm

        ct_fdb.load_tables(folder_name, join_tb_list)
        emm = ct_fdb.construct_index()
        addjoin_size_fdb.append(len(pickle.dumps(emm, -1)))
        del emm

    for x, y in zip(original_size_fdb, addrange_size_fdb):
        ratio_rg_fdb.append(Decimal((y - x) / x).quantize(Decimal("0.00")))

    for x, y in zip(original_size_fdb, addjoin_size_fdb):
        ratio_jo_fdb.append(Decimal((y - x) / x).quantize(Decimal("0.00")))

    return [original_size_fdb, addrange_size_fdb, ratio_rg_fdb, ratio_jo_fdb]


if __name__ == '__main__':
    test_folder = ["../data/sf0.001"]
    # test_folder = ["../data/sf0.002"]
                   # "../data/sf0.004", "../data/sf0.005", "../data/sf0.006",
                   # "../data/sf0.007", "../data/sf0.008", "../data/sf0.009",
                   # "../data/sf0.01"]
    tb_list = ["lineitem"]
    rg_tb_list = ["lineitem_rg"]
    join_tb_list = ["lineitem_join"]

    test_result = test_storage_size(test_folder, tb_list,
                                    rg_tb_list, join_tb_list)

    data_frame = pd.DataFrame({
        "Scale": [x.split("/")[2] for x in test_folder],
        "Original Size FInEDB": test_result[0],
        "Modified Size FInEDB": test_result[1],
        "Expand Ratio FInEDB (range)": test_result[2],
        "Expand Ratio FInEDB (join)": test_result[3]
    })
    data_frame.to_csv("./3-JOIN-Storage.csv", index=False)
