from subprocess import check_output


def main():
    c_value = "0.2"
    sample_file_train = "Sample_Files/train_all_best"
    temp_model = "Models/model_all.data"
    check_output(["./svm_rank_learn", "-c", c_value, sample_file_train, temp_model])

    c_value = "0.2"
    sample_file_train = "Sample_Files/train_29_best"
    temp_model = "Models/model_29.data"
    check_output(["./svm_rank_learn", "-c", c_value, sample_file_train, temp_model])
if __name__ == '__main__':
    main()
