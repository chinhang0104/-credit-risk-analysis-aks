## Start of AKS ##

# https://docs.microsoft.com/en-us/azure/aks/spark-job
connect_to_aks:
	az aks get-credentials --resource-group msbd5003 --name msbd5003-aks
	kubectl get nodes
	kubectl create serviceaccount spark
	kubectl create clusterrolebinding spark-role --clusterrole=edit  --serviceaccount=default:spark --namespace=default

# https://spark.apache.org/docs/latest/running-on-kubernetes.html#docker-images
# https://towardsdatascience.com/how-to-build-spark-from-source-and-deploy-it-to-a-kubernetes-cluster-in-60-minutes-225829b744f9
build_spark_image_for_aks:
	# git clone https://github.com/apache/spark.git --branch v3.0.1
	# spark image
	spark/bin/docker-image-tool.sh -r spark-on-k8s -t v3.0.1 build
	# pyspack support
	spark/bin/docker-image-tool.sh -r pyspark-on-k8s -t v3.0.1 -p spark/resource-managers/kubernetes/docker/src/main/dockerfiles/spark/bindings/python/Dockerfile build

push_spark_image_to_acr:
	# docker rmi msbd5003registry.azu	recr.io/pyspark-on-k8s:v3.0.1
	docker tag pyspark-on-k8s/spark-py:v3.0.1 msbd5003registry.azurecr.io/pyspark-on-k8s:v3.0.1
	docker push msbd5003registry.azurecr.io/pyspark-on-k8s:v3.0.1
	az acr repository list --name msbd5003registry --output table

submit_example_pyspark_job:
	# upload the spark job file to azure storage
	az storage blob upload --account-name msbd5003storage --container-name sparkjobs --file spark_jobs/example.py --name example.py
	./spark-submit-aks.sh

# create a spark cluster
# connect to the spark cluster from my local machine 

# spark streaming
# https://stackoverflow.com/questions/54785519/using-airflow-to-run-spark-streaming-jobs
# figure out how to have spark streaming in production

# airflow deployment

# airflow submits pyspark job:
# https://campus.datacamp.com/courses/building-data-engineering-pipelines-in-python/managing-and-orchestrating-a-workflow?ex=8

# hbase cluster
# write & read data from hbase
