"""
This file provides code to create .let files. These files contain the instances for which we will extract features.
As the codes are developed for ARQMath dataset, each line is in the format of:
Topic id, visual id, score -- One might use formula id instead of visual id.

Note: read_qrel_file reads the qrel file (training or all topics) to create the LtR model, but the result file
is just used for re-ranking not training SVM model, so the scores are not important.
"""
import pandas as pd


def read_qrel_file(file_path):
    """
    reading qrel file into dictionary of topic id: dictionary of visual id:score
    file_path: qrel file path
    result: dictionary of topic ids: (dictionary of visual ids: scores)
    """
    df = pd.read_csv(file_path, header=None, sep='\t')
    result = {}
    for row in df.iterrows():
        topic_id = row[1][0]
        visual_id = row[1][2]
        score = row[1][3]
        if topic_id in result:
            result[topic_id][visual_id] = score
        else:
            result[topic_id] = {visual_id: score}
    return result


def read_result_file(result_file):
    """
        NOTE: Based on the result file format one might change the indices
        reading qrel file into dictionary of topic id: dictionary of visual id:score
        file_path: qrel file path
        result: dictionary of topic ids: (dictionary of visual ids: scores)
    """
    df = pd.read_csv(result_file, header=None, sep='\t')
    result = {}
    for row in df.iterrows():
        topic_id = row[1][0]
        visual_id = row[1][2]
        score = row[1][4]
        if topic_id in result:
            result[topic_id][visual_id] = score
        else:
            result[topic_id] = {visual_id: score}
    return result


def create_letor_file(let_file, read_file, is_qrel):
    "Create letor from qrel or result file"
    if is_qrel:
        all_topics = read_qrel_file(read_file)
    else:
        all_topics = read_result_file(read_file)
    file = open(let_file, "w")
    for topic_id in all_topics:
        dic_temp = all_topics[topic_id]
        for visual_id in dic_temp:
            score = dic_temp[visual_id]
            file.write(str(topic_id) + "\t" + str(visual_id) + "\t" + str(score) + "\n")
    file.close()


# create_letor_file("let_qrel.tsv", "qrel_v_2.tsv", True)
create_letor_file("let_tangent_2020.tsv", "tangent_2020_v.tsv", False)
