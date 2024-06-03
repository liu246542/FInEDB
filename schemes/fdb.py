#!/usr/bin/python3

import pickle
from collections import namedtuple
from utils.tools import gen_key, prf_256, BFF,\
    ParseRawData, bxor, bxor2, prf_any
from utils.REMM import REMM
from utils import TDAG
from bitarray import util as bitutil

SecretKey = namedtuple("SecretKey", ["K_T", "K_S", "K_J"])

Table_Relations = {
    "customer/_id": ["c_id_o_custkey"],
    "customer/C_NATIONKEY": ["c_nationkey_nation_id"],
    "lineitem/L_ORDERKEY": ["l_orderkey_order_id"],
    "lineitem/L_PARTKEY": ["l_partkey_part_id"],
    "lineitem/L_SUPPKEY": ["l_suppkey_supplier_id"],
    "nation/_id": ["c_nationkey_nation_id", "s_nationkey_nation_id"],
    "nation/N_REGIONKEY": ["n_regionkey_region_id"],
    "orders/_id": ["l_orderkey_order_id"],
    "orders/O_CUSTKEY": ["c_id_o_custkey"],
    "part/_id": ["l_partkey_part_id", "p_id_partsupp_ps_partkey"],
    "partsupp/PS_PARTKEY": ["p_id_partsupp_ps_partkey"],
    "partsupp/PS_SUPPKEY": ["ps_suppkey_supplier_id"],
    "regin/_id": ["n_regionkey_region_id"],
    "supplier/_id": ["ps_suppkey_supplier_id", "l_suppkey_supplier_id"],
    "supplier/S_NATIONKEY": ["s_nationkey_nation_id"]
}


class Client(object):
    """docstring for Client"""

    def __init__(self, lamba=256, SK=None):
        if SK is None:
            # SK = (K_T, K_S, K_J)
            self.SK = SecretKey(*[gen_key(lamba) for i in range(3)])
        else:
            self.SK = SK

    def load_tables(self, folder_name, table_name_list):
        Raw_Tables = list(map(lambda x: ParseRawData(folder_name, x, 1),
                              table_name_list))
        print("-" * 20 + "LOAD COMPLETE" + "-" * 20)
        self.Raw_Tables = Raw_Tables

    def __gen_bff__(self, table_info, sk, Node_Index):
        temp_dict = {}
        temp_inverted_index = {}
        (t_name, t_data, t_type) = table_info
        (K_e, K_v, K_J) = sk
        nonce = str(gen_key(8))
        bff = BFF(nonce=nonce)
        for row in t_data.iterrows():
            row_dict = row[1].to_dict()
            label = t_name + "_id" + str(row_dict["_id"])
            bff_rest = bff.construct(row_dict, K_e, K_v, K_J,
                                     self.SK.K_T, t_data.columns,
                                     t_type, Node_Index)
            (flag, value, tdict, bff_info) = bff_rest
            if flag == 0:
                return False
            temp_dict.setdefault(label, [])
            temp_dict[label].append(value)
            temp_inverted_index.update(tdict)
        return (temp_dict, temp_inverted_index, bff_info)

    def construct_index(self, test_flag=0):
        # Raw_Tables => inverted index (BFF inside)
        inverted_index = {}
        if test_flag:
            filter_dict = {}  # only for test, not need in Scheme
        bff_dict = {}  # store in the client's side
        tdag_dict = {}  # store in the client's side
        remm = REMM()
        K_J = self.SK.K_J
        for table_info in self.Raw_Tables:
            (t_name, t_data, t_type) = table_info

            Node_Index = {}

            for i, t in enumerate(t_type):
                if t == 2:
                    attr = t_data.columns[i]
                    value_list = list(t_data[attr])

                    max_value = max(value_list)
                    tdag = TDAG.TDAG(max_value)
                    tdag_dict.setdefault(t_name + attr, max_value)
                    (MM_range, node_dict) = tdag.construct(value_list)

                    for node_name in MM_range.keys():
                        v_list = MM_range.get(node_name)

                        label = t_name + attr + "rg" + node_name
                        value = [t_name + attr + str(x) for x in v_list]

                        inverted_index.setdefault(label, value)

                    Node_Index.setdefault(attr, (node_dict, max_value))

            K_e = prf_256(self.SK.K_S, t_name)  # K_1
            K_v = prf_256(self.SK.K_T, t_name)  # K_2

            # Integrate Binary Fuse filters
            # Start -----------------------
            for i in range(100):
                f = self.__gen_bff__(table_info, (K_e, K_v, K_J),
                                     Node_Index)
                if f is not False:
                    break
                if i == 99 and f is False:
                    raise RuntimeError("Fail to generate a BFF")
            inverted_index.update(f[0])
            inverted_index.update(f[1])
            bff_dict.setdefault(t_name, f[2])
            if test_flag:
                filter_dict.update(f[0])
            # raise RuntimeError("break")
            # End -------------------------

            for row in t_data.iterrows():
                row_dict = row[1].to_dict()
                for attr in t_data.columns:
                    if attr == "_id":
                        continue
                    else:
                        # For those attributes are not "_id"
                        label = attr + str(row_dict[attr])
                        # label = prf_256(self.SK.K_T, label)
                        value = t_name + "_id" + str(row_dict["_id"])
                    inverted_index.setdefault(label, [])
                    inverted_index[label].append(value)
        emm = remm.setup(inverted_index, self.SK.K_T)
        self.bff_dict = bff_dict
        self.tdag_dict = tdag_dict
        if test_flag:
            filter_emm = remm.setup(filter_dict, self.SK.K_T)
            return (emm, filter_emm)
        return emm

    def gen_token(self, query_tuple, table_name):
        q1_label = query_tuple.Where[0] + str(query_tuple.Value[0])
        stag = prf_256(self.SK.K_T, q1_label)
        tk1 = stag

        tk3 = []
        bff_info = self.bff_dict.get(table_name)
        N = bff_info.length * bff_info.number
        bff = BFF(nonce=bff_info.nonce)
        for select_att in query_tuple.Select:
            init_select = bitutil.zeros(N)
            K_v = prf_256(self.SK.K_T, table_name)
            query_label = str(prf_256(K_v, select_att + "SELECT"))
            pos_list = bff.resolve_position(query_label,
                                            bff_info.length,
                                            bff_info.number)
            for p in pos_list:
                init_select[p] = 1
            tk3.append(bitutil.sc_encode(init_select))

        tk2 = []
        sum_where = 0
        sum_val = 0
        for where_att, where_val in zip(query_tuple.Where,
                                        query_tuple.Value):
            init_where = bitutil.zeros(N)

            K_v = prf_256(self.SK.K_T, table_name)
            query_label = str(prf_256(K_v, where_att + "WHERE"))
            bff = BFF()
            pos_list = bff.resolve_position(query_label,
                                            bff_info.length,
                                            bff_info.number)
            # query_label =
            for p in pos_list:
                init_where[p] = 1
            sum_where = bxor2(sum_where, init_where)

            init_val = prf_any(K_v, str(where_val), 4)
            sum_val = bxor(sum_val, init_val)

            tk2.append((bitutil.sc_encode(sum_where), sum_val))
        return (tk1, tk2, tk3)


if __name__ == '__main__':
    ct = Client()
    # print(ct.SK.K_T)
    tb_list = ["customer", "lineitem", "nation", "orders",
               "part", "partsupp", "region", "supplier"]
    # tb_list = ["customer"]
    ct.load_tables("../data/sf0.01", tb_list)
    emm = ct.construct_index()
    # print(pysize.get_size(emm))
    print(len(pickle.dumps(emm, -1)))
