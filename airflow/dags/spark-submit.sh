# delete previous pod
kubectl delete pods --ignore-not-found=true credit-driver

# spark submit
# /usr/spark/bin/spark-submit \
# --master k8s://https://msbd5003-aks-dns-1ede652a.hcp.eastus.azmk8s.io:443 \
# --deploy-mode cluster \
# --name credit \
# --conf spark.executor.instances=3 \
# --conf spark.kubernetes.driver.pod.name=credit-driver \
# --conf spark.kubernetes.driver.request.cores=1 \
# --conf spark.kubernetes.driver.limit.cores=1 \
# --conf spark.kubernetes.executor.request.cores=1 \
# --conf spark.kubernetes.executor.limit.cores=1 \
# --conf spark.kubernetes.container.image=msbd5003registry.azurecr.io/msbd5003-pyspark:latest \
# --conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
# --conf spark.kubernetes.report.interval=10s \
# https://msbd5003storage.blob.core.windows.net/sparkjobs/credit.py



/usr/spark/bin/spark-submit \
--master k8s://https://msbd5003-aks-dns-1ede652a.hcp.eastus.azmk8s.io:443 \
--deploy-mode cluster \
--name credit \
--conf spark.executor.instances=4 \
--conf spark.kubernetes.driver.pod.name=credit-driver \
--conf spark.kubernetes.driver.request.cores=1.2 \
--conf spark.kubernetes.driver.limit.cores=1.2 \
--conf spark.kubernetes.executor.request.cores=1.2 \
--conf spark.kubernetes.executor.limit.cores=1.2 \
--conf spark.kubernetes.container.image=msbd5003registry.azurecr.io/msbd5003-pyspark-2:1.0.2 \
--conf spark.kubernetes.authenticate.driver.serviceAccountName=spark \
--conf spark.kubernetes.report.interval=10s \
https://msbd5003storage.blob.core.windows.net/sparkjobs/training.py


echo "=========================================================="
echo "Relavent Logs:"
echo "=========================================================="

# Get relavent logs
kubectl logs credit-driver | grep "INFO __main__:"

# Check if the spark job failed or not
if kubectl get pods credit-driver --output="jsonpath={.status.phase}" | grep -q 'Succeeded'; then
    exit 0
else
    exit 1
fi