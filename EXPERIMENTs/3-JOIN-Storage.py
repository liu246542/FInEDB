#!/usr/bin/python3

import pickle
import pandas as pd
from decimal import Decimal
from functools import partial
from multiprocessing import Pool
from schemes import spx, fdb


def atom_process_task(folder_name, tb_list):
    emm_size = []

    ct_fdb = fdb.Client()
    ct_fdb.load_tables(folder_name, tb_list)
    emm = ct_fdb.construct_index(test_flag=1)
    emm_size.append(len(pickle.dumps(emm[0], -1)))
    emm_size.append(len(pickle.dumps(emm[1], -1)))
    del ct_fdb, emm

    ct_spx = spx.Client()
    ct_spx.load_tables(folder_name, tb_list)
    emm = ct_spx.construct_index()
    emm_size.append(len(pickle.dumps(emm, -1)))
    for e in emm:
        emm_size.append(len(pickle.dumps(e, -1)))
    del ct_spx, emm

    return emm_size


def bytes2MB(x):
    return Decimal(x / 1048576).quantize(Decimal("0.00"))


def test_storage_size(folder_list, tb_list):
    disk_size_fdb = []
    filter_size_fdb = []
    disk_size_spx = []

    EMM_R_size = []
    EMM_C_size = []
    EMM_V_size = []
    EDX_size = []

    with Pool() as p:
        size_list = p.map(partial(atom_process_task,
                                  tb_list=tb_list), folder_list)

    for size_tuple in size_list:
        disk_size_fdb.append(size_tuple[0])
        filter_size_fdb.append(size_tuple[1])
        disk_size_spx.append(size_tuple[2])
        EMM_R_size.append(size_tuple[3])
        EMM_C_size.append(size_tuple[4])
        EMM_V_size.append(size_tuple[5])
        EDX_size.append(size_tuple[6])

    return (disk_size_fdb, filter_size_fdb, disk_size_spx,
            EMM_R_size, EMM_C_size, EMM_V_size, EDX_size)


if __name__ == '__main__':
    test_folder = ["../data/sf0.001", "../data/sf0.002",
                   "../data/sf0.003", "../data/sf0.004",
                   "../data/sf0.005", "../data/sf0.006",
                   "../data/sf0.007", "../data/sf0.008",
                   "../data/sf0.009", "../data/sf0.01"]

    test_folder = ["../data/sf0.005", "../data/sf0.006",
                   "../data/sf0.007", "../data/sf0.008",
                   "../data/sf0.009", "../data/sf0.01"]
    # tb_list = ["customer", "lineitem", "nation"]
    tb_list = ["customer", "lineitem", "nation", "orders",
               "part", "partsupp", "region", "supplier"]
    join_tb_list = [x + "_join" for x in tb_list]

    original_result = test_storage_size(test_folder, tb_list)
    addjoin_result = test_storage_size(test_folder, join_tb_list)

    ratio_fdb = []
    for x, y in zip(original_result[0], addjoin_result[0]):
        ratio_fdb.append(Decimal((y - x) / x).quantize(Decimal("0.00")))

    ratio_spx = []
    for x, y in zip(original_result[2], addjoin_result[2]):
        ratio_spx.append(Decimal((y - x) / x).quantize(Decimal("0.00")))

    data_frame = pd.DataFrame({
        "Scale": [x.split("/")[2] for x in test_folder],
        "FInEDB Size": [bytes2MB(x) for x in original_result[0]],
        "Filter": [bytes2MB(x) for x in original_result[1]],
        "FInEDB Join Size": [bytes2MB(x) for x in addjoin_result[0]],
        "Filter Join": [bytes2MB(x) for x in addjoin_result[1]],
        "Ratio FInEDB": ratio_fdb,
        "SPX Size": [bytes2MB(x) for x in original_result[2]],
        "EMM_R": [bytes2MB(x) for x in original_result[3]],
        "EMM_C": [bytes2MB(x) for x in original_result[4]],
        "EMM_V": [bytes2MB(x) for x in original_result[5]],
        "EDX": [bytes2MB(x) for x in original_result[6]],
        "SPX Join Size": [bytes2MB(x) for x in addjoin_result[2]],
        "EMM_R Join": [bytes2MB(x) for x in addjoin_result[3]],
        "EMM_C Join": [bytes2MB(x) for x in addjoin_result[4]],
        "EMM_V Join": [bytes2MB(x) for x in addjoin_result[5]],
        "EDX Join": [bytes2MB(x) for x in addjoin_result[6]],
        "Ratio SPX": ratio_spx
    })
    data_frame.to_csv("./3-JOIN-Storage-9-10.csv", index=False)
    print(data_frame)
