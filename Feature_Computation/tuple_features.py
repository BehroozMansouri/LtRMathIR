import csv
import os
import sys

from TangentS.Tuple_Extraction import math_ml_to_node, harmonic_prec_recall
from Feature_Computation.arqmath_topic_reader import TopicReader


class TextEmbedding:
    def __init__(self, topic_file_path, letor_file, math_ml_collection, math_ml_queries, is_slt):
        self.topic_reader = TopicReader(topic_file_path)
        self.map_query_list_formulas = self.read_letor_file(letor_file)
        self.mathml_collection = self.__read_formula_files(math_ml_collection)
        self.mathml_queries = self.__read_formula_files_queries(math_ml_queries)
        self.map_query_id_trees = self.mathml_queries
        self.dictioney_query_id_result_trees = self.__get_results_tree()

    def read_letor_file(self, letor_file):
        result = {}
        with open(letor_file, newline='', encoding="utf-8") as csv_file:
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
            with open(formula_index_directory_path + "/" + filename, newline='', encoding="utf-8") as csv_file:
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

    def __read_result(self, result_file_path):
        dictionary_query_result_formula_id_lst = {}
        with open(result_file_path, newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
            next(csv_reader)
            for row in csv_reader:
                query_id = row[0]
                formula_id = int(row[1])
                if query_id in dictionary_query_result_formula_id_lst:
                    dictionary_query_result_formula_id_lst[query_id].append(formula_id)
                else:
                    dictionary_query_result_formula_id_lst[query_id] = [formula_id]
        return dictionary_query_result_formula_id_lst

    def __get_queries_tree(self, is_slt):
        result = {}
        for topic_id in self.mathml_queries:
            math_ml = self.mathml_queries[topic_id]
            try:
                tree = math_ml_to_node(math_ml, is_slt)
            except:
                print("this topic failed: " + str(topic_id))
                print("this mathml: " + str(math_ml))
                continue
            result[topic_id] = tree
        return result

    def __get_results_tree(self, ):
        map_result = {}
        for topic_id in self.map_query_list_formulas:
            lst_result = self.map_query_list_formulas[topic_id]
            current_map = {}
            for formula_id in lst_result:
                if formula_id not in self.mathml_collection:
                    print("not found: " + str(formula_id))
                    continue
                math_ml = self.mathml_collection[formula_id]
                current_map[formula_id] = math_ml
            map_result[topic_id] = current_map
        return map_result

    def reranking_results(self, is_slt, is_type):
        dic_res_tuples = {}
        for topic_id in self.map_query_list_formulas:
            result_map_tuple = self.__rerank_query(self.dictioney_query_id_result_trees[topic_id],
                                                   self.map_query_id_trees[topic_id], is_slt, is_type)
            dic_res_tuples[topic_id] = result_map_tuple
        return dic_res_tuples

    def __rerank_query(self, map_tree_formulas, query_mathml, is_slt, is_type):
        result_map_inverse = {}
        temp_dic = {
            "<csymbol cd=\"mws\" name=\"qvar\">qvar_$</csymbol>": "",
            "<csymbol cd=\"latexml\">differential-d</csymbol>": "<ci>d</ci>",
            "<csymbol cd=\"latexml\">double-factorial</csymbol>": "<ci>df</ci>",
            "<csymbol cd=\"latexml\">implied-by</csymbol>": "<ci>ib</ci>",
            "<csymbol cd=\"latexml\">conditional</csymbol>": "<ci>c</ci>",
            "<csymbol cd=\"mws\" name=\"qvar\">qvar_</csymbol>": "",

        }
        counter = 1
        for formula in map_tree_formulas:
            counter += 1
            try:
                formula_mathml = map_tree_formulas[formula]
                for item in temp_dic:
                    formula_mathml = formula_mathml.replace(item, temp_dic[item], formula_mathml.count(item))
                    query_mathml = query_mathml.replace(item, temp_dic[item], query_mathml.count(item))
                harmonic_mean = harmonic_prec_recall(formula_mathml, query_mathml, is_slt, is_type)
                result_map_inverse[formula] = harmonic_mean
            except:
                print("----------------")
                print(formula_mathml)
                pass
        return result_map_inverse


def get_tuple_features(let_file, home_dir, feature_dir, topic_file, year):
    csv.field_size_limit(sys.maxsize)
    presentations = ["opt", "slt"]
    types = [False, True]
    for presentation in presentations:
        for ty in types:
            formula_rep = presentation
            is_type = ty
            if formula_rep == "slt":
                is_slt = True
            else:
                is_slt = False

            text_em = TextEmbedding(topic_file, let_file,
                                    home_dir + formula_rep + "_representation_v2",
                                    home_dir + "Formula_topics_" + formula_rep + "_" + year + ".tsv",
                                    is_slt=is_slt)

            dic_res_tuples = text_em.reranking_results(is_slt, is_type)

            with open(feature_dir + "tuple_" + formula_rep + '_' + str(is_type) + '.tsv', mode='w') as csv_file:
                csv_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
                for topic_id in text_em.map_query_list_formulas:
                    for formula_id in text_em.map_query_list_formulas[topic_id]:
                        result_map = dic_res_tuples[topic_id]
                        if formula_id in result_map:
                            csv_writer.writerow([topic_id, formula_id, dic_res_tuples[topic_id][formula_id]])
                        else:
                            print(str(topic_id) + "\t" + str(formula_id))
                            csv_writer.writerow([topic_id, formula_id, 0])
