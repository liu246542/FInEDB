#!/usr/bin/python3

import pickle
import pandas as pd
from schemes import spx, fdb
# from utils import pysize


def test_storage_size(folder_list, tb_list):
    # memo_size_fdb = []
    disk_size_fdb = []
    # memo_size_spx = []
    disk_size_spx = []
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
    return (disk_size_fdb, disk_size_spx)


if __name__ == '__main__':
    test_folder = ["../data/sf0.001", "../data/sf0.002", "../data/sf0.003"]
                   # "../data/sf0.004", "../data/sf0.005", "../data/sf0.006",
                   # "../data/sf0.007", "../data/sf0.008", "../data/sf0.009",
                   # "../data/sf0.01"]
    tb_list = ["customer", "lineitem", "nation", "orders",
               "part", "partsupp", "region", "supplier"]
    # (m_f, d_f, m_s, d_s) = test_storage_size(test_folder, tb_list)
    (d_f, d_s) = test_storage_size(test_folder, tb_list)
    data_frame = pd.DataFrame({
        "Scale": [x.split("/")[2] for x in test_folder],
        # "Memory Size FInEDB": m_f,
        "Disk Size FInEDB": d_f,
        # "Memory Size SPX": m_s,
        "Disk Size SPX": d_s
    })
    data_frame.to_csv("./1-EQ-Storage.csv", index=False)
