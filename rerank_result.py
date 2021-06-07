from subprocess import check_output


def read_letor_result_file(file_path):
    file = open(file_path)
    lst_result = []
    line = file.readline().strip()
    while line:
        lst_result.append(float(line))
        line = file.readline().strip()
    return lst_result


def read_sample_file(file_path):
    file = open(file_path)
    line = file.readline().strip()
    lst_result = []
    while line:
        q_id = line.split(" ")[1]
        topic_id = "B."+q_id.split(":")[1]
        visual_id = line.split("#")[1]
        lst_result.append((topic_id, visual_id))
        line = file.readline().strip()
    return lst_result


def create_sample_file_result(sample_file, ranked_result, result_file):
    lst_topic_query_ids = read_sample_file(sample_file)
    score_values = read_letor_result_file(ranked_result)
    result = {}
    for i in range(len(lst_topic_query_ids)):
        query_id = lst_topic_query_ids[i][0]
        visual_id = lst_topic_query_ids[i][1]
        score = score_values[i]
        if query_id in result:
            result[query_id][visual_id] = score
        else:
            result[query_id] = {visual_id: score}
    file = open(result_file, "w")
    for query_id in result:
        dic_visual_id_score = result[query_id]
        sort_orders = dict(sorted(dic_visual_id_score.items(), key=lambda x: x[1], reverse=True))
        rank = 1
        for item in sort_orders:
            file.write(query_id + "\tQ0\t" + item + "\t" + str(rank) + "\t" + str(sort_orders[item]) + "\tRun0\n")
            rank += 1
    file.close()
    return result


def main():
    sample_file_test = "Sample_Files/sam_2021"
    temp_model = "Models/model_all.data"
    ranked_result_svm = "ranked.tsv"

    check_output(["./svm_rank_classify", sample_file_test, temp_model, ranked_result_svm])
    # writing trec_formatted file
    ranked_result_trec = "reranked_2021_all.tsv"
    create_sample_file_result(sample_file_test, ranked_result_svm, ranked_result_trec)

    # sample_file_test = "Sample_Files/sam_2021"
    # temp_model = "Models/model_29.data"
    # ranked_result_svm = "ranked.tsv"
    #
    # check_output(["./svm_rank_classify", sample_file_test, temp_model, ranked_result_svm])
    # # writing trec_formatted file
    # ranked_result_trec = "reranked_2021_29.tsv"
    # create_sample_file_result(sample_file_test, ranked_result_svm, ranked_result_trec)

if __name__ == '__main__':
    main()
