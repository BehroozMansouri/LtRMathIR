import csv
import os
import numpy
import torch

from scipy import spatial
from Feature_Computation.arqmath_topic_reader import TopicReader
use_cuda = torch.cuda.is_available()
print(use_cuda)


class TextEmbedding:
    def __init__(self, topic_file_path, base_file_path, letor_file, file_id):
        self.file_id = file_id
        print("loading model")
        print("reading files")
        self.topic_reader = TopicReader(topic_file_path)
        self.topic_vectors = self.get_topic_vectors(base_file_path)
        self.formula_vectors = self.get_formula_vectors(base_file_path)
        self.pairs = self.read_letor_file(letor_file)

        self.final_result = {}
        for topic_id in self.pairs:
            query_vec = self.topic_vectors[topic_id].reshape(1, 300)
            temp_dic = {}
            for item in self.pairs[topic_id]:
                if item in self.formula_vectors:
                    formula_vec = self.formula_vectors[item].reshape(1, 300)
                    cosine = 1 - spatial.distance.cosine(query_vec, formula_vec)
                else:
                    cosine = -1
                temp_dic[item] = cosine
            self.final_result[topic_id] = temp_dic

    def get_topic_vectors(self, base_file_path):
        map_topics = {}
        formula_vectors = numpy.load(base_file_path+"/formula_s_"+self.file_id+".npy")
        i = 0
        for topic_id in self.topic_reader.map_topics:
            map_topics[topic_id] = formula_vectors[i].reshape(1, 300)
            i += 1
        return map_topics

    def get_formula_vectors(self, base_file_path):
        result_formulas = {}
        for i in range(1, 10):
            title_vectors = numpy.load(base_file_path + "/a_"+self.file_id+"/" + str(i) + ".npy")
            file = open(base_file_path + "/am_"+self.file_id+"/" + str(i))
            line = file.readline().strip()
            while line:
                row_id = int(line.split("\t")[0])
                question_id = int(line.split("\t")[1])
                title_vector = title_vectors[row_id].reshape(1, 300)
                result_formulas[question_id] = title_vector
                line = file.readline().strip()
        return result_formulas

    def read_letor_file(self, letor_file):
        result = {}
        with open(letor_file, newline='') as csv_file:
            csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
            for row in csv_reader:
                topic_id = row[0]
                formula_1 = int(row[1])
                if topic_id in result:
                    result[topic_id].append(formula_1)
                else:
                    result[topic_id] = [formula_1]
        for topic_id in result:
            result[topic_id] = list(set(result[topic_id]))
        return result


def main(let_file, embedding_file):
    file_ids = ["100", "102", "104", "105"]
    for file_id in file_ids:
        text_embedding = TextEmbedding("Topics_V1.1.xml", embedding_file,
                                       let_file, file_id)
        with open("../Feature_Files/embedding_"+file_id, mode='w') as csv_file:
            csv_writer = csv.writer(csv_file, delimiter='\t', quotechar='"', quoting=csv.QUOTE_MINIMAL)
            for topic_id in text_embedding.final_result:
                for formula_id in text_embedding.final_result[topic_id]:
                    csv_writer.writerow([topic_id, formula_id, str(text_embedding.final_result[topic_id][formula_id])])


if __name__ == '__main__':
    let_file = "../let_all.tsv"
    embedding_file = "/home/bm3302/ArqMath_Task1/TangentCFT/"
    main(let_file, embedding_file)
