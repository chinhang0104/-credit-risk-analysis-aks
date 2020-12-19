# credit-risk-analysis-aks

Credit Risk Analysis with Spark on Azure Kubernetes Service (AKS)

Data Source: https://www.kaggle.com/c/home-credit-default-risk/data

1. Experiment Notebook: MSBD5003 Project Experimentws.ipynb

- it contains code for the Feature Engineering and Machine Learning Experiments

2. spark_clusters/jobs: these are codes for spark-submit

- streaming.py: it contains the code for using Spark Streaming to do resources filtering and inserting them into MongoDB
- training.py: it contains the code for training model on Spark Cluster

3. spark_clusters/streaming_cluster:

- it contains the setup script for setting up the streaming application.

4. spark_clusters/one_time_cluster:

- it contains the Dockerfile entry point we used to deploy the K8s Spark cluster.

5. Makefile:

- it contains the commands we used to build deployment images, uploading resources and deployment.

6. airflow/dags:

- trainging.py: it is the daily Airflow DAB definition file.
- spart-submit.sh: it is the script for submitting spark job from Airflow.

7. Dash-plotly: it contains the code for setting up the visualization server.
