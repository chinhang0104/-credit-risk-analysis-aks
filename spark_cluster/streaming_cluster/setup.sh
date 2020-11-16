# ssh -i spark-vm-ssh.pem msbd5003@52.136.122.181
# ssh -i spark-vm-ssh.pem  azureuser@52.149.217.95
# ssh -i spark-vm-ssh.pem azureuser@40.87.111.122

# from master
# ssh azureuser@msbd5003-spark-1
# ssh azureuser@msbd5003-spark-2


sudo apt-get update \
    && sudo apt-get install -y wget \
    && sudo apt-get install -y software-properties-common \
    && sudo add-apt-repository ppa:openjdk-r/ppa \
    && sudo apt-get update \
    && sudo apt-get install -y openjdk-8-jdk \
    && sudo apt-get install -y python3-pip \
    && sudo rm -rf /var/lib/apt/lists/*


wget -nv https://archive.apache.org/dist/spark/spark-3.0.0/spark-3.0.0-bin-hadoop2.7.tgz \
    && tar xf spark-3.0.0-bin-hadoop2.7.tgz

mv "spark-3.0.0-bin-hadoop2.7" "spark"

wget https://apache.01link.hk/hadoop/common/hadoop-2.9.2/hadoop-2.9.2.tar.gz

tar xf hadoop-2.9.2.tar.gz
mv "hadoop-2.9.2" "hadoop"

....

# spark submit
HADOOP_HOME=$HOME/hadoop \
LD_LIBRARY_PATH=$HOME/hadoop/lib/native:$LD_LIBRARY_PATH \
PYSPARK_PYTHON=python3 spark/bin/spark-submit \
    --master spark://msbd5003-spark-0.qkn3qgj4eqmejkxq4udkgnthmd.bx.internal.cloudapp.net:7077 \
	--name streaming \
	--packages org.mongodb.spark:mongo-spark-connector_2.12:3.0.0 \
    --conf 'spark.mongodb.input.uri=mongodb://xxx' \
	--conf 'spark.mongodb.output.uri=mongodb://xxx' \
    ~/streaming.py





