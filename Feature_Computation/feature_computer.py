from Feature_Computation.cft_features import get_cft_features
from Feature_Computation.tangent_s_features import get_tangents_features
from Feature_Computation.ted_features import get_ted_features
from Feature_Computation.tuple_features import get_tuple_features


def calculate_features_tangent_s(year):
    # year = "2020"
    let_file = "../CreateInstances/let_tangents_" + year + ".tsv"
    feature_dir = "../Feature_Files/tangent_" + year + "/"
    topic_file = "Topics_Task2_" + year + ".xml"

    get_tangents_features(let_file, feature_dir, "../tangent_s_reranked/slt_" + year + "_reranked.tsv",
                          "../tangent_s_reranked/opt_" + year + "_reranked.tsv")
    print("tangents: done")
    get_tuple_features(let_file, "/home/bm3302/", feature_dir, topic_file, year)
    print("tuple: done")
    get_ted_features(let_file, "/home/bm3302/", feature_dir, topic_file, year)
    print("ted: done")
    get_cft_features(let_file, "/home/bm3302/ArqMath_Task1/TangentCFT/", feature_dir, topic_file, year)
    print("cft: done")


def calculate_features_qrel():
    year = "2020"
    let_file = "../CreateInstances/let_qrel.tsv"
    feature_dir = "../Feature_Files/qrel_2020/"
    topic_file = "Topics_Task2_" + year + ".xml"

    get_tangents_features(let_file, feature_dir, "../tangent_s_reranked/slt_qrel_reranked.tsv",
                          "../tangent_s_reranked/opt_qrel_reranked.tsv")
    print("tangents: done")
    get_tuple_features(let_file, "/home/bm3302/", feature_dir, topic_file, year)
    print("tuple: done")
    get_ted_features(let_file, "/home/bm3302/", feature_dir, topic_file, year)
    print("ted: done")
    get_cft_features(let_file, "/home/bm3302/ArqMath_Task1/TangentCFT/", feature_dir, topic_file, year)
    print("cft: done")


# calculate_features_qrel()
# calculate_features_tangent_s("2020")
calculate_features_tangent_s("2021")