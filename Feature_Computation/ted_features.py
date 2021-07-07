import csv
import os
import sys

from Feature_Computation.arqmath_topic_reader import TopicReader
from TangentS.Tuple_Extraction import math_ml_to_node
from apted.helpers import Tree
from apted import APTED, PerEditOperationConfig




class TextEmbedding:
    def __init__(self, topic_file_path, letor_file, math_ml_collection, math_ml_queries, is_slt, is_type, has_edge,
                 weight):
        print("loading model")
        print("reading files")
        self.topic_reader = TopicReader(topic_file_path)
        self.map_query_list_formulas = self.read_letor_file(letor_file)
        self.mathml_collection = self.__read_formula_files(math_ml_collection)
        self.mathml_queries = self.__read_formula_files_queries(math_ml_queries)
        self.map_query_id_trees = self.__get_queries_tree(is_slt, is_type, has_edge)
        self.dictioney_query_id_result_trees = self.__get_results_tree(is_slt, is_type, has_edge)
        self.weight = weight

    def read_letor_file(self, letor_file):
        result = {}
        with open(letor_file, newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
            for row in csv_reader:
                topic_id = row[0]
                visual_id = int(row[1])
                if topic_id in result:
                    result[topic_id].append(visual_id)
                else:
                    result[topic_id] = [visual_id]
        for topic_id in result:
            result[topic_id] = list(set(result[topic_id]))
        return result

    def __read_formula_files(self, formula_index_directory_path):
        dictionary_formula_id = {}
        for filename in os.listdir(formula_index_directory_path):
            with open(formula_index_directory_path + "/" + filename, newline='') as csv_file:
                csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
                next(csv_reader)
                for row in csv_reader:
                    visual_id = int(row[4])
                    math_ml = row[5]
                    dictionary_formula_id[visual_id] = math_ml
        return dictionary_formula_id

    def __read_formula_files_queries(self, formula_index_directory_path):
        dictionary_formula_id = {}
        with open(formula_index_directory_path, newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
            next(csv_reader)
            for row in csv_reader:
                formula_id = row[0]
                math_ml = row[4]
                dictionary_formula_id[formula_id] = math_ml
        result = {}
        for item in self.topic_reader.map_topics:
            result[self.topic_reader.map_topics[item].topic_id] = \
                dictionary_formula_id[self.topic_reader.map_topics[item].formula_id]
        return result

    def __get_queries_tree(self, is_slt, is_type, has_edges):
        result = {}
        temp_dic = {
            "<csymbol cd=\"mws\" name=\"qvar\">qvar_$</csymbol>": "",
            "<csymbol cd=\"latexml\">differential-d</csymbol>": "<ci>d</ci>",
            "<csymbol cd=\"latexml\">conditional</csymbol>": "<ci>c</ci>",
            "<csymbol cd=\"mws\" name=\"qvar\">qvar_</csymbol>": "",
        }

        for topic_id in self.mathml_queries:
            math_ml = self.mathml_queries[topic_id]
            for item in temp_dic:
                math_ml = math_ml.replace(item, temp_dic[item], math_ml.count(item))
            # try:
            tree = math_ml_to_node(math_ml, is_slt, is_type, has_edges)
            result[topic_id] = tree
            # except:
            #     print("this topic failed: " + str(topic_id))
            #     print("this mathml: " + str(math_ml))
        return result

    def __get_results_tree(self, is_slt, is_type, has_edges):
        map_result = {}
        for topic_id in self.map_query_list_formulas:
            lst_result = self.map_query_list_formulas[topic_id]
            current_map = {}
            for formula_id in lst_result:
                if formula_id not in self.mathml_collection:
                    continue

                math_ml = self.mathml_collection[formula_id]
                temp_dic = {
                    "<csymbol cd=\"mws\" name=\"qvar\">qvar_$</csymbol>": "",
                    "<csymbol cd=\"latexml\">differential-d</csymbol>": "<ci>d</ci>",
                    "<csymbol cd=\"latexml\">conditional</csymbol>": "<ci>c</ci>",
                    "<csymbol cd=\"mws\" name=\"qvar\">qvar_</csymbol>": ""
                }
                for item in temp_dic:
                    math_ml = math_ml.replace(item, temp_dic[item], math_ml.count(item))
                try:
                    tree = math_ml_to_node(math_ml, is_slt, is_type, has_edges)
                except:
                    continue
                if tree is None:
                    continue
                current_map[formula_id] = tree
            map_result[topic_id] = current_map
        return map_result

    def reranking_results(self, is_slt):
        dic_res_inverse = {}
        dic_res_node = {}
        print("reading files done...")
        for topic_id in self.map_query_list_formulas:
            result_map_inverse, result_map_node = self.__rerank_query(self.dictioney_query_id_result_trees[topic_id],
                                                                      self.map_query_id_trees[topic_id], is_slt)
            dic_res_inverse[topic_id] = result_map_inverse
            dic_res_node[topic_id] = result_map_node
        return dic_res_inverse, dic_res_node

    def __rerank_query(self, map_tree_formulas, query_tree, is_slt):
        result_map_inverse = {}
        result_map_node = {}
        for formula in map_tree_formulas:
            try:
                formula_tree = map_tree_formulas[formula]
                lst = [query_tree, formula_tree]
                if lst is None:
                    print(formula)
                    continue
                tree1, tree2 = map(Tree.from_text, lst)
                if self.weight:
                    if is_slt:
                        apted = APTED(tree1, tree2, PerEditOperationConfig(9, 1, 8))  # del_cost, ins_cost, ren_cost
                    else:
                        apted = APTED(tree1, tree2, PerEditOperationConfig(8, 1, 5))
                else:
                    apted = APTED(tree1, tree2, PerEditOperationConfig(1, 1, 1))

                ted = apted.compute_edit_distance()
                result_map_inverse[formula] = 1 / (ted + 1)

                if self.weight:
                    if is_slt:
                        apted = APTED(tree1, tree2, PerEditOperationConfig(4, 2, 4))  # del_cost, ins_cost, ren_cost
                    else:
                        apted = APTED(tree1, tree2, PerEditOperationConfig(3, 2, 2))
                else:
                    apted = APTED(tree1, tree2, PerEditOperationConfig(1, 1, 1))

                ted = apted.compute_edit_distance()
                ted = ted / 10

                #### INVERSE TED
                result_map_inverse[formula] = 1 / (ted + 1)

                n1 = query_tree.count("{")
                n2 = formula_tree.count("{")
                normalized_ted = ted / (n1 + n2)

                #### NODE NORMALIZED
                result_map_node[formula] = 1.0 - normalized_ted  # math.exp(-normalized_ted)   #1/(ted+1)#
            except:
                print(formula)
                pass
        result_map_inverse = {k: v for k, v in sorted(result_map_inverse.items(), key=lambda item: item[1],
                                                      reverse=True)}
        result_map_node = {k: v for k, v in sorted(result_map_node.items(), key=lambda item: item[1],
                                                   reverse=True)}
        return result_map_inverse, result_map_node


def get_ted_features(let_file, home_dir, feature_dir, topic_file, year):
    csv.field_size_limit(sys.maxsize)
    presentations = ["opt", "slt"]
    types = [False, True]
    weighted = [False, True]
    for presentation in presentations:
        for ty in types:
            for weight in weighted:
                formula_rep = presentation
                is_type = ty
                if formula_rep == "slt":
                    is_slt = True
                else:
                    is_slt = False
                if is_type:
                    t = "t"
                else:
                    t = ""
                if weight:
                    w = "w"
                else:
                    w = ""
                text_em = TextEmbedding(topic_file, let_file,
                                        home_dir + formula_rep + "_representation_v2",
                                        home_dir + "Formula_topics_" + formula_rep + "_" + year + ".tsv",
                                        is_slt=is_slt, is_type=is_type, has_edge=False, weight=weight)
                dic_res_inverse, dic_res_node = text_em.reranking_results(is_slt)
                with open(feature_dir + 'ted_' + formula_rep + '_' + w + t + '.tsv', mode='w') as csv_file:
                    csv_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                    for topic_id in text_em.map_query_list_formulas:
                        for formula_id in text_em.map_query_list_formulas[topic_id]:
                            result_map = dic_res_node[topic_id]
                            if formula_id in result_map:
                                csv_writer.writerow([topic_id, formula_id, dic_res_node[topic_id][formula_id]])
                            else:
                                csv_writer.writerow([topic_id, formula_id, 0])
