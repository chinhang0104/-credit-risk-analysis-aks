## Start of AKS ##

# https://docs.microsoft.com/en-us/azure/aks/spark-job
connect_to_aks:
	az aks get-credentials --resource-group msbd5003 --name msbd5003-aks
	kubectl get nodes
	kubectl create serviceaccount spark
	kubectl create clusterrolebinding spark-role --clusterrole=edit  --serviceaccount=default:spark --namespace=default

# https://spark.apache.org/docs/latest/running-on-kubernetes.html#docker-images
# https://towardsdatascience.com/how-to-build-spark-from-source-and-deploy-it-to-a-kubernetes-cluster-in-60-minutes-225829b744f9
# git clone https://github.com/apache/spark.git --branch v3.0.1
build_spark_image_for_aks:
	# spark image
	spark/bin/docker-image-tool.sh -r spark-on-k8s -t v3.0.1 build
	# pyspack support
	spark/bin/docker-image-tool.sh -r pyspark-on-k8s -t v3.0.1 -p spark/resource-managers/kubernetes/docker/src/main/dockerfiles/spark/bindings/python/Dockerfile build
	docker build spark_cluster -t msbd5003-pyspark


push_spark_image_to_acr: build_spark_image_for_aks
	az acr login --name msbd5003registry
	docker tag msbd5003-pyspark:latest msbd5003registry.azurecr.io/msbd5003-pyspark:latest
	docker push msbd5003registry.azurecr.io/msbd5003-pyspark:latest
	az acr repository list --name msbd5003registry --output table

submit_example_pyspark_job:
	# upload the spark job file to azure storage
	az storage blob upload --account-name msbd5003storage --container-name sparkjobs --file spark_cluster/jobs/example.py --name example.py
	
	# delete previous pod
	# kubectl delete pods example-driver

	# spark submit
	spark/bin/spark-submit \
	--master k8s://https://msbd5003-aks-dns-1ede652a.hcp.eastus.azmk8s.io:443 \
	--deploy-mode cluster \
	--name example \
	--conf spark.executor.instances=2 \
	--conf spark.kubernetes.driver.request.cores=1 \
	--conf spark.kubernetes.driver.limit.cores=1 \
	--conf spark.kubernetes.executor.request.cores=1 \
	--conf spark.kubernetes.executor.limit.cores=1 \
	--conf spark.kubernetes.container.image=msbd5003registry.azurecr.io/msbd5003-pyspark:latest \
	--conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
	--conf spark.kubernetes.report.interval=10s \
	https://msbd5003storage.blob.core.windows.net/sparkjobs/example.py
	
	# Get all logs
	kubectl logs example-driver

	echo "=========================================================="
	echo "Relavent Logs:"
	echo "=========================================================="

	# Get relavent logs
	kubectl logs example-driver | grep "INFO __main__:"

## Start of Airflos

build_airflow_image_for_aks:
	# airflow image 
	# --no-cache
	docker build airflow -t msbd5003-airflow 

push_airflow_image_to_acr: build_airflow_image_for_aks
	az acr login --name msbd5003registry
	docker tag msbd5003-airflow:latest msbd5003registry.azurecr.io/msbd5003-airflow:latest
	docker push msbd5003registry.azurecr.io/msbd5003-airflow:latest
	az acr repository list --name msbd5003registry --output table

# https://docs.bitnami.com/tutorials/deploy-apache-airflow-azure-postgresql-redis/
# https://github.com/bitnami/charts/tree/master/bitnami/airflow
deploy_airflow: push_airflow_image_to_acr
	helm upgrade airflow-aks airflow-stable/airflow \
	--values ./airflow/values.yaml
	kubectl rollout restart deploy airflow-aks-web
	kubectl rollout restart deploy airflow-aks-scheduler
	# http://40.88.192.26:8080/

proxy_airflow:
	 kubectl port-forward --namespace default svc/airflow-aks-web 8091:8080

## End of Airflow

# airflow submits pyspark job:
# https://campus.datacamp.com/courses/building-data-engineering-pipelines-in-python/managing-and-orchestrating-a-workflow?ex=8

# hbase cluster
# https://cloud.google.com/blog/products/databases/to-run-or-not-to-run-a-database-on-kubernetes-what-to-consider

# spark streaming
# https://stackoverflow.com/questions/54785519/using-airflow-to-run-spark-streaming-jobs
# figure out how to have spark streaming in production

# kubectl delete pods --field-selector status.phase=Failed