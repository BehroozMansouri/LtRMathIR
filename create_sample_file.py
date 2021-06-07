import csv
import os


def read_result_files(file_path):
    samples = {}
    with open(file_path, newline='') as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t', quotechar='"')
        for row in csv_reader:
            topic_id = int(row[0].split(".")[1])
            score = float(row[2])
            if score == -1:
                score = 0
            if topic_id in samples:
                samples[topic_id][row[1]] = score
            else:
                samples[topic_id] = {row[1]: score}
    return samples


def read_other_features(file_path):
    result = {}
    with open(file_path, mode='r', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        for row in csv_reader:
            topic_id = int(row[0].split(".")[1])
            visual_id = row[1]
            if topic_id in result:
                result[topic_id][visual_id] = row[2:]
            else:
                result[topic_id] = {visual_id: row[2:]}
    lst_dic = []
    for i in range(0, 7):
        temp_dic = {}
        for topic_id in result:
            temp_dic2 = {}
            current_dic = result[topic_id]
            for visual_id in current_dic:
                temp_dic2[visual_id] = current_dic[visual_id][i]
            temp_dic[topic_id] = temp_dic2
        lst_dic.append(temp_dic)
    return lst_dic


def read_feature_files(dir_path, include_other_feature):
    values = []
    for file in os.listdir(dir_path):
        print(file)
        if file == "other_features.tsv":
            if include_other_feature:
                lst_dics = read_other_features(dir_path + file)
                for dic in lst_dics:
                    values.append(dic)
        else:
            values.append(read_result_files(dir_path+file))
    return values


def read_letor_file(letor_file):
    """
    Takes in a letor file path, and reads it into a dictionary
    each line represents a topic id \t visual id \t score
    """
    dic_formula_latex = {}
    with open(letor_file, mode='r', encoding="utf-8") as csv_file:
        csv_reader = csv.reader(csv_file, delimiter='\t')
        for row in csv_reader:
            topic_id = int(row[0].split(".")[1])
            visual_id = row[1]
            score = float(row[2])
            if topic_id in dic_formula_latex:
                if score in dic_formula_latex[topic_id]:
                    dic_formula_latex[topic_id][score].append(visual_id)
                else:
                    dic_formula_latex[topic_id][score] = [visual_id]
            else:
                dic_formula_latex[topic_id] = {score: [visual_id]}
    return dic_formula_latex


def get_samples(let_file, feature_directory, include_other_feature=False, is_train=False):
    """
    This method creates sample file for the cornell and other learning to rank models
    let_file: file path to instances that will be used to l2r
    feature_directory: directory in which the feature files are located
    include_other_feature: indicates whether or not to include the other tree-related feature
    """
    # reading the sample topic and visual ids
    dic_visual_ids_score = read_letor_file(let_file)
    # reading the features files
    lst_feature_dic = read_feature_files(feature_directory, include_other_feature)

    samples = []
    for topic_id in sorted(dic_visual_ids_score):
        topic = topic_id
        dic_lists = dic_visual_ids_score[topic_id]
        # Iteration over different scores
        for i in dic_lists:
            lst_visual_ids = dic_lists[i]
            if is_train:
                score = str(i)
            else:
                score = str(0)
            for visual_id in lst_visual_ids:
                current_feature_vec = []
                for feature in lst_feature_dic:
                    current_feature = 0
                    if topic_id in feature:
                        dic_current_topic = feature[topic_id]
                        if visual_id in dic_current_topic:
                            current_feature = dic_current_topic[visual_id]
                        else:
                            print(visual_id)
                            current_feature = 0
                    current_feature_vec.append(current_feature)

                count = 1
                temp_string = score + " qid:" + str(topic)
                for feature in current_feature_vec:
                    temp_string += " " + str(count) + ":" + str(feature)
                    count += 1
                samples.append(temp_string + "#" + str(visual_id))
    return samples


def create_sample_file(let_file, feature_directory, result_file, include_other_feature):
    samples = get_samples(let_file=let_file, feature_directory=feature_directory,
                          include_other_feature=include_other_feature)
    file = open(result_file, "w")
    for line in samples:
        file.write(line + "\n")
    file.close()


def main():
    """
    Create the sample files that will be used for training RankSVM and then the sample file for actual ranking.
    """
    # feature_directory = "Feature_Files/qrel_2020/"
    # let_file = "CreateInstances/let_qrel.tsv"
    # create_sample_file(let_file, feature_directory, "Sample_Files/train_all_best", False)
    #
    # feature_directory = "Feature_Files/qrel_2020/"
    # let_file = "CreateInstances/let_29.tsv"
    # create_sample_file(let_file, feature_directory, "Sample_Files/train_29_best", False)

    # feature_directory = "Feature_Files/tangent_2020/"
    # let_file = "CreateInstances/let_tangent_2020.tsv"
    # create_sample_file(let_file, feature_directory, "Sample_Files/sam_2020", False)

    feature_directory = "Feature_Files/tangent_2021/"
    let_file = "CreateInstances/let_tangent_2021.tsv"
    create_sample_file(let_file, feature_directory, "Sample_Files/sam_2021", False)

if __name__ == '__main__':
    main()
