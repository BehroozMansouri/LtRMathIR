# LtRMathIR
Codes for SIGIR 2021 paper Learning to Rank for Mathematical Formula Retrieval
### Create Instance
We need formula instances to train our model and also for re-ranking. If used for training it is important to specify the query, formula instance id and relevance score
### Feature Computation
After the instances are determine, the next step is to computer the similarity features. This is done in Feature_computation directory
### Create SVM-Rank Sample File
Once the similarity measures are calculated, we have to provide sample file to use for SVM-Rank. This done by running create_sample_file.py
### Train Model
To train svm-rank model, run train_model.py. Please make sure you have SVM_rank already installed.
### Re-rank Results
After SVM-rank model is trained, use rerank_result.py to rerank you retrieval result.
