from subprocess import check_output


def main():
    c_value = "0.2"
    sample_file_train = "create_sample_files/sample_29"
    sample_file_test = "create_sample_files/sample_45"
    temp_model = "model.data"
    ranking_result = "ranked.tsv"
    check_output(["./svm_rank_learn", "-c", c_value, sample_file_train, temp_model])

    check_output(["./svm_rank_classify", sample_file_test, temp_model, ranking_result])


if __name__ == '__main__':
    main()
