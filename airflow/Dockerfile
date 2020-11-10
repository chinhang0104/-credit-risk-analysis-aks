FROM apache/airflow:1.10.12-python3.6

USER root

RUN update-ca-certificates -f \
  && apt-get update \
  && apt-get upgrade -y \
  && apt-get install -y \
    wget \
    git \
    libatlas3-base \
    libopenblas-base \
  && apt-get clean

# java scala
RUN apt-get install default-jdk scala git -y

# spark
RUN cd /usr/ \
    && wget "https://downloads.apache.org/spark/spark-3.0.1/spark-3.0.1-bin-hadoop2.7.tgz" \
    && tar xzf spark-3.0.1-bin-hadoop2.7.tgz \
    && rm spark-3.0.1-bin-hadoop2.7.tgz \
    && mv spark-3.0.1-bin-hadoop2.7 spark


ENV SPARK_HOME /usr/spark
ENV PATH="/usr/spark/bin:${PATH}"
ENV SPARK_MAJOR_VERSION 3
ENV PYTHONPATH=$SPARK_HOME/python/lib/py4j-0.10.4-src.zip:$SPARK_HOME/python/:$PYTHONPATH

# NOTE: dag path is set with the `dags.path` value
COPY ./dags dags

USER airflow
