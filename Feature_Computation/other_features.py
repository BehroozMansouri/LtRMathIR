import csv
import os
import sys
import numpy
import numpy as np
from collections import Counter
from Feature_Computation.arqmath_topic_reader import TopicReader
from TangentS.Tree_generator_tool import TreeCreator
from TangentS.Tuple_Extraction import math_ml_to_node2, math_ml_tuples


def get_collection_data(file_path):
    file = open(file_path)
    result = {}
    line = file.readline().strip()
    while line:
        parts = line.split("\t")
        topic_id = parts[0]
        visual_id = int(parts[1])
        if topic_id in result:
            result[topic_id].append(visual_id)
        else:
            result[topic_id] = [visual_id]
        line = file.readline().strip()
    return result


def read_formula_files(formula_index_directory_path, is_slt):
    dictionary_formula = {}
    for filename in os.listdir(formula_index_directory_path):
        with open(formula_index_directory_path + "/" + filename, newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
            next(csv_reader)
            for row in csv_reader:
                visual_id = int(row[4])
                the_type = row[3]
                if the_type == "comment":
                    continue
                math_ml = row[5]
                if not is_slt:
                    temp_dic = {
                        "<csymbol cd=\"mws\" name=\"qvar\">qvar_$</csymbol>": "",
                        "<csymbol cd=\"latexml\">differential-d</csymbol>": "<ci>d</ci>",
                        "<csymbol cd=\"latexml\">conditional</csymbol>": "<ci>c</ci>",
                        "<csymbol cd=\"mws\" name=\"qvar\">qvar_</csymbol>": "",
                        "<csymbol cd=\"latexml\">double-factorial</csymbol>": "<ci>d</ci>",
                        "<csymbol cd=\"latexml\">implied-by</csymbol>": "<ci>i</ci>",
                    }
                    for item in temp_dic:
                        math_ml = math_ml.replace(item, temp_dic[item], math_ml.count(item))
                dictionary_formula[visual_id] = math_ml
    return dictionary_formula


def simi(lst_ops_q, lst_ops_c):
    c = list((Counter(lst_ops_q) & Counter(lst_ops_c)).elements())
    max_length = max(len(lst_ops_q), len(lst_ops_c))
    if max_length == 0:
        max_length = 1
    return len(c) / max_length


def get_elements(root_query):
    if root_query.lst_children is None or len(root_query.lst_children) == 0:
        node_type = root_query.value.split("!")[0]
        value = root_query.value.split("!")[1]
        if node_type is "V":
            return [], [], [value]
        elif node_type is "N":
            return [value], [], []
        elif node_type is "U" or node_type is "O":
            return [], [value], []
        else:
            return [], [], []
    else:
        lst_num, lst_op, lst_var = [], [], []
        for child in root_query.lst_children:
            print(root_query.lst_children)
            print(child)
            num, op, var = get_elements(child)
            lst_num = lst_num + num
            lst_op = lst_op + op
            lst_var = lst_var + var
        if "!" not in root_query.value:
            return lst_num, lst_op, lst_var
        node_type = root_query.value.split("!")[0]
        value = root_query.value.split("!")[1]
        if node_type is "V":
            lst_var.append(value)
            return lst_num, lst_op, lst_var
        elif node_type is "N":
            lst_num.append(value)
            return lst_num, lst_op, lst_var
        elif node_type is "U" or node_type is "O":
            lst_op.append(value)
            return lst_num, lst_op, lst_var
        else:
            return [], [], []


def get_matching(candidate_tuples, q_opt_tuples):
    root_query = TreeCreator.tuples_to_tree(q_opt_tuples)
    root_candidate = TreeCreator.tuples_to_tree(candidate_tuples)
    lst_num_q, lst_ops_q, lst_vars_q = get_elements(root_query)
    lst_num_c, lst_ops_c, lst_vars_c = get_elements(root_candidate)
    o = simi(lst_ops_q, lst_ops_c)
    n = simi(lst_num_q, lst_num_c)
    v = simi(lst_vars_q, lst_vars_c)
    return o, n, v


class TextEmbedding:
    def __init__(self, topic_file_path, math_ml_queries, is_slt, let_file, tsv_file_base):
        print("loading model")
        print("reading files")
        self.topic_reader = TopicReader(topic_file_path)
        self.mathml_queries = self.__read_formula_files_queries(math_ml_queries)
        self.collection = get_collection_data(let_file)
        if not is_slt:
            self.mathml_collection = read_formula_files(tsv_file_base+"opt_representation_v2", is_slt)
        else:
            self.mathml_collection = read_formula_files(tsv_file_base+"slt_representation_v2", is_slt)
        self.map_query_trees, self.map_query_depth, self.map_query_vars = self.__get_queries_tree(is_slt)
        self.map_collection_trees, self.map_collection_depth, self.map_collection_vars = self.__get_collection_tree(
            is_slt)
        self.map_query_tuples = self.__get_queries_tuples(is_slt)
        self.map_collection_tuples = self.__get_collection_tuples(is_slt)

    def __read_formula_files_queries(self, formula_index_directory_path):
        dictionary_formula_id = {}
        with open(formula_index_directory_path, newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
            next(csv_reader)
            for row in csv_reader:
                formula_id = row[0]
                math_ml = row[4]
                temp_dic = {
                    "<csymbol cd=\"mws\" name=\"qvar\">qvar_$</csymbol>": "",
                    "<csymbol cd=\"latexml\">differential-d</csymbol>": "<ci>d</ci>",
                    "<csymbol cd=\"latexml\">conditional</csymbol>": "<ci>c</ci>",
                    "<csymbol cd=\"mws\" name=\"qvar\">qvar_</csymbol>": "",
                }
                for item in temp_dic:
                    math_ml = math_ml.replace(item, temp_dic[item], math_ml.count(item))
                dictionary_formula_id[formula_id] = math_ml
        result = {}
        for item in self.topic_reader.map_topics:
            result[self.topic_reader.map_topics[item].topic_id] = \
                dictionary_formula_id[self.topic_reader.map_topics[item].formula_id]
        return result

    def __get_queries_tree(self, is_slt):
        result = {}
        res_depth = {}
        res_vars = {}
        for topic_id in self.mathml_queries:
            math_ml = self.mathml_queries[topic_id]
            tree, depth, variation = math_ml_to_node2(math_ml, is_slt)
            result[topic_id] = tree
            res_depth[topic_id] = depth
            res_vars[topic_id] = variation
        return result, res_depth, res_vars

    def __get_collection_tree(self, is_slt):
        result = {}
        res_depth = {}
        res_vars = {}
        for topic_id in self.collection:
            lst_visual_ids = self.collection[topic_id]
            for visual_id in lst_visual_ids:
                if visual_id not in self.mathml_collection:
                    continue
                try:
                    math_ml = self.mathml_collection[visual_id]
                    tree, depth, variation = math_ml_to_node2(math_ml, is_slt)
                    result[visual_id] = tree
                    res_depth[visual_id] = depth
                    res_vars[visual_id] = variation
                except:
                    continue
        return result, res_depth, res_vars

    def __get_queries_tuples(self, is_slt):
        result = {}
        for topic_id in self.mathml_queries:
            math_ml = self.mathml_queries[topic_id]
            tuples = math_ml_tuples(math_ml, is_slt)
            temp_tuple = []
            for tuple in tuples:
                temp_tuple.append(tuple.split("\t"))
            result[topic_id] = temp_tuple
        return result

    def __get_collection_tuples(self, is_slt):
        result = {}
        for topic_id in self.collection:
            lst_visual_ids = self.collection[topic_id]
            for visual_id in lst_visual_ids:
                if visual_id not in self.mathml_collection:
                    print(visual_id)
                    continue
                try:
                    math_ml = self.mathml_collection[visual_id]
                    tuples = math_ml_tuples(math_ml, is_slt)
                    temp_tuple = []
                    for tuple in tuples:
                        temp_tuple.append(tuple.split("\t"))
                    result[visual_id] = temp_tuple
                except:
                    continue
        return result


def calculate_other_features(let_file, tsv_file_dir):
    csv.field_size_limit(sys.maxsize)

    formula_rep = "opt"
    text_em = TextEmbedding("Topics_V1.1.xml",
                            "/home/bm3302/Formula_topics_" + formula_rep + "_V3.0.tsv",
                            is_slt=False, let_file=let_file, tsv_file_base= tsv_file_dir)
    q_tree_opt = text_em.map_query_trees
    q_depth_opt = text_em.map_query_depth
    c_tree_opt = text_em.map_collection_trees
    c_depth_opt = text_em.map_collection_depth
    q_tuples_opt = text_em.map_query_tuples
    c_tuples_opt = text_em.map_collection_tuples

    formula_rep = "slt"
    text_em = TextEmbedding("Topics_V1.1.xml",
                            "/home/bm3302/Formula_topics_" + formula_rep + "_V3.0.tsv",
                            is_slt=True, let_file=let_file, tsv_file_base= tsv_file_dir)
    q_tree_slt = text_em.map_query_trees
    q_var_slt = text_em.map_query_vars

    c_tree_slt = text_em.map_collection_trees
    c_var_slt = text_em.map_collection_vars
    dic_topic_lst_visual_ids = text_em.collection

    "Creating features"
    final_res = {}
    for query_id in dic_topic_lst_visual_ids:
        lst_visual_ids = dic_topic_lst_visual_ids[query_id]
        q_opt_tuples = q_tuples_opt[query_id]
        "Reading query features"
        node_opt = q_tree_opt[query_id].count("{")
        depth_opt = q_depth_opt[query_id]
        node_slt = q_tree_slt[query_id].count("{")
        var_slt = q_var_slt[query_id]
        lst_query_feature = numpy.array([node_opt, node_slt, depth_opt, var_slt])
        "Reading candidate features"
        temp_dic = {}
        for visual_id in lst_visual_ids:
            if visual_id in c_tree_opt:
                node_opt = c_tree_opt[visual_id].count("{")
                depth_opt = c_depth_opt[visual_id]
            else:
                node_opt = 0
                depth_opt = 0
            if visual_id in c_tree_slt:
                node_slt = c_tree_slt[visual_id].count("{")
                var_slt = c_var_slt[visual_id]
            else:
                node_slt = 0
                var_slt = 0

            if visual_id in c_tuples_opt:
                candidate_tuples = c_tuples_opt[visual_id]
                o, n, v = get_matching(candidate_tuples, q_opt_tuples)
            else:
                o, n, v = 0, 0, 0

            temp_lst = numpy.array([node_opt, node_slt, depth_opt, var_slt])
            temp_dic[visual_id] = abs((lst_query_feature - temp_lst) / (lst_query_feature + 1))
            temp_dic[visual_id] = np.append(temp_dic[visual_id], (o,n,v))

        final_res[query_id] = temp_dic

    with open('../Feature_Files/other_features.tsv', mode='w') as csv_file:
        csv_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        for query_id in final_res:
            temp_dic = final_res[query_id]
            values = list(temp_dic.values())
            a = np.array(values, dtype=int)
            max_values_list = a.max(axis=0)
            min_values_list = a.min(axis=0)
            for visual_id in temp_dic:
                lst_values = temp_dic[visual_id]
                temp_list = []
                for i in range(0, len(lst_values)):
                    x = max_values_list[i] - min_values_list[i]
                    if x == 0:
                        x = 1
                    temp_list.append((lst_values[i] - min_values_list[i]) / x)
                csv_writer.writerow([query_id, visual_id] + temp_list)

