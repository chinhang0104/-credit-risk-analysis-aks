FROM apache/airflow:1.10.12-python3.6

RUN pwd
RUN ls dags

# NOTE: dag path is set with the `dags.path` value
COPY ./dags dags

RUN ls dags
