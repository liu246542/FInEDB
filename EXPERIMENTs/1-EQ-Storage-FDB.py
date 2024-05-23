#!/usr/bin/python3

import pickle
import pandas as pd
from decimal import Decimal
from functools import partial
from multiprocessing import Pool
from schemes import fdb
# from utils import pysize


def atom_process_task(folder_name, tb_list):
    emm_size = []

    ct_fdb = fdb.Client()
    ct_fdb.load_tables(folder_name, tb_list)
    emm = ct_fdb.construct_index(test_flag=1)
    emm_size.append(len(pickle.dumps(emm[0], -1)))
    emm_size.append(len(pickle.dumps(emm[1], -1)))
    del ct_fdb, emm

    return emm_size


def test_storage_size(folder_list, tb_list):
    # memo_size_fdb = []
    disk_size_fdb = []
    filter_size_fdb = []
    # memo_size_spx = []

    # size_list = list(map(partial(atom_process_task,
                                 # tb_list=tb_list), folder_list))
    with Pool() as p:
        size_list = p.map(partial(atom_process_task,
                                  tb_list=tb_list), folder_list)

    for size_tuple in size_list:
        disk_size_fdb.append(size_tuple[0])
        filter_size_fdb.append(size_tuple[1])

    """
    for folder_name in folder_list:
        ct_fdb = fdb.Client()
        ct_fdb.load_tables(folder_name, tb_list)
        emm = ct_fdb.construct_index()
        # memo_size_fdb.append(pysize.get_size(emm))
        disk_size_fdb.append(len(pickle.dumps(emm, -1)))
        del ct_fdb, emm

        ct_spx = spx.Client()
        ct_spx.load_tables(folder_name, tb_list)
        emm = ct_spx.construct_index()
        # memo_size_spx.append(pysize.get_size(emm))
        disk_size_spx.append(len(pickle.dumps(emm, -1)))
        del ct_spx, emm
    """
    return (disk_size_fdb, filter_size_fdb)


if __name__ == '__main__':
    test_folder = ["../data/sf0.01", "../data/sf0.1"]
                   # "../data/sf0.004", "../data/sf0.005", "../data/sf0.006",
                   # "../data/sf0.007", "../data/sf0.008", "../data/sf0.009",
                   # "../data/sf0.01"]
    tb_list = ["customer", "lineitem", "nation", "orders",
               "part", "partsupp", "region", "supplier"]
    # (m_f, d_f, m_s, d_s) = test_storage_size(test_folder, tb_list)
    (d_f, f_s) = test_storage_size(test_folder, tb_list)
    data_frame = pd.DataFrame({
        "Scale": [x.split("/")[2] for x in test_folder],
        # "Memory Size FInEDB": m_f,
        # "Disk Size FInEDB": d_f,
        "Disk Size FInEDB": [Decimal(x / 1048576).quantize(Decimal("0.00"))
                             for x in d_f],
        "Filter Size FInEDB": [Decimal(x / 1048576).quantize(Decimal("0.00"))
                               for x in f_s]
        # "Memory Size SPX": m_s,
        # "Disk Size SPX": d_s
    })
    # data_frame.to_csv("./1-EQ-Storage.csv", index=False)
    print(data_frame)
