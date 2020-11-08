# delete previous pod
kubectl delete pods example-driver

# spark submit
spark/bin/spark-submit \
--master k8s://https://msbd5003-aks-dns-1ede652a.hcp.eastus.azmk8s.io:443 \
--deploy-mode cluster \
--name example \
--conf spark.kubernetes.driver.pod.name=example-driver \
--conf spark.executor.instances=2 \
--conf spark.kubernetes.container.image=msbd5003registry.azurecr.io/pyspark-on-k8s:v3.0.1 \
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