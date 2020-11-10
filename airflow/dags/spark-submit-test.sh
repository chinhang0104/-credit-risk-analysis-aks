# delete previous pod
kubectl delete pods --ignore-not-found=true example-driver

# spark submit
/usr/spark/bin/spark-submit \
--master k8s://https://msbd5003-aks-dns-1ede652a.hcp.eastus.azmk8s.io:443 \
--deploy-mode cluster \
--name example \
--conf spark.executor.instances=2 \
--conf spark.kubernetes.driver.pod.name=example-driver \
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