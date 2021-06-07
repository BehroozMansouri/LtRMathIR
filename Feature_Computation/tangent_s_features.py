def read_reranked_file(file_path):
    file = open(file_path, encoding="utf-8")
    file.readline().strip()
    line = file.readline().strip()
    mss = {}
    negative_with_unification = {}
    negative_without_unification = {}
    while line:
        parts = line.split("\t")
        if parts[0] == "Q":
            current_topic = parts[1]
            line = file.readline().strip()
        else:
            visual_id = parts[1]
            scores = parts[4]
            scores = scores[1:-1]
            scores = scores.split(",")
            if current_topic in mss:
                mss[current_topic][visual_id] = scores[0]
            else:
                mss[current_topic] = {visual_id: scores[0]}
            if current_topic in negative_with_unification:
                negative_with_unification[current_topic][visual_id] = scores[1]
            else:
                negative_with_unification[current_topic] = {visual_id: scores[1]}
            if current_topic in negative_without_unification:
                negative_without_unification[current_topic][visual_id] = scores[2]
            else:
                negative_without_unification[current_topic] = {visual_id: scores[2]}
        line = file.readline().strip()
        if not line:
            line = file.readline().strip()
    return mss, negative_with_unification, negative_without_unification


def read_letor(param):
    file = open(param, encoding="utf-8")
    line = file.readline().strip()
    res = {}
    while line:
        parts = line.split("\t")
        query = parts[0]
        visual_id = parts[1]
        score = parts[2]
        if query in res:
            res[query][visual_id] = score
        else:
            res[query] = {visual_id: score}
        line = file.readline().strip()
    return res


def write_features(result_file_path, let_dic, feature_dic):
    file = open(result_file_path, "w")
    for topic_id in let_dic:
        current_map = let_dic[topic_id]
        for visual_id in current_map:
            if topic_id in feature_dic and visual_id in feature_dic[topic_id]:
                file.write(topic_id + "\t" + visual_id + "\t" + feature_dic[topic_id][visual_id] + "\n")
            else:
                file.write(topic_id + "\t" + visual_id + "\t0\n")
    file.close()


def get_tangents_features(let_file, feature_dir, reranked_slt, reranked_opt):
    mss, negative_with_unification, negative_without_unification = read_reranked_file(reranked_slt)
    mss2, negative_with_unification2, negative_without_unification2 = read_reranked_file(reranked_opt)
    let_map = read_letor(let_file)

    write_features(feature_dir + "align_slt", let_map, mss)
    write_features(feature_dir + "align_opt", let_map, mss2)
    write_features(feature_dir + "slt_node", let_map, negative_without_unification)
    write_features(feature_dir + "opt_node", let_map, negative_without_unification2)
    write_features(feature_dir + "slt_type_node", let_map, negative_with_unification)
    write_features(feature_dir + "opt_type_node", let_map, negative_with_unification2)
