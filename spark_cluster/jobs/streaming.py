from pyspark import SparkContext, SparkConf
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as sf
import json
from datetime import datetime


def _push(collection_name, df):
    df.cache()
    logger.warn(f"Pushing {df.count()} {collection_name} to db")

    start = datetime.now()

    df.write.format("mongo").mode("append").option("database", "credit").option("collection", collection_name).save()
    
    end = datetime.now()
    spent = (end - start).total_seconds()
    logger.warn(f"Pushed, spent {spent} seconds")

def _handle_jsons(rdd):
    # transform lines to jsons
    df = spark.read.json(rdd)
    df.cache()
    
    # classify
    applications = df.filter(df["type"]=="application")
    applications.cache()
    prev_applications = df.filter(df["type"]=="prev_application")
    prev_applications.cache()
    installments = df.filter(df["type"]=="installment")
    installments.cache()

    start = datetime.now()
    logger.warn(f"Recieved {df.count()} records at {start}")
    
    _df = installments.select("data").rdd.flatMap(lambda x:x).toDF(sampleRatio=0.01) 
    _df = _df.withColumn('_id', sf.concat(
                                        sf.col('SK_ID_PREV'), sf.lit('-'),
                                        sf.col('NUM_INSTALMENT_VERSION'), sf.lit('-'),
                                        sf.col('NUM_INSTALMENT_NUMBER'))
                                        )
    _push("installment", _df)
       
    
    _df = prev_applications.select("data").rdd.flatMap(lambda x:x).toDF(sampleRatio=0.1) 
    _df = _df.withColumn('_id', _df["SK_ID_PREV"])
    _push("prev_application", _df)
    
    _df = applications.select("data").rdd.flatMap(lambda x:x).toDF(sampleRatio=0.1) 
    _df = _df.withColumn('_id', _df["SK_ID_CURR"])
    _push("application", _df)
    
    end = datetime.now()
    spent = (end - start).total_seconds()
    logger.warn(f"Handled this batch, spent {spent} seconds at {end}")
    



spark = SparkSession \
    .builder \
    .appName("credit_stream") \
    .getOrCreate()

sc = spark.sparkContext

log4jLogger = sc._jvm.org.apache.log4j 
logger = log4jLogger.LogManager.getLogger(__name__) 
logger.warn("Start streaming")

# Create a queue of RDDs
rdd = sc.textFile('./stream.ndjson', 8)

    
logger.warn("Started")

# split the rdd into 5 equal-size parts
rddQueue = rdd.randomSplit([1.0]*1000, 123)
        
# Create a StreamingContext with batch interval of 5 seconds
ssc = StreamingContext(sc, 60)

# Feed the rdd queue to a DStream
lines = ssc.queueStream(rddQueue)

results = lines.foreachRDD(_handle_jsons)
ssc.start()
ssc.awaitTermination()
ssc.stop(False)

logger.warn("Finished")