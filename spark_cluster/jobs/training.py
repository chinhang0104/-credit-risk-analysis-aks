from pyspark import SparkContext, SparkConf, SparkFiles
from pyspark.streaming import StreamingContext
from pyspark.sql import SparkSession
from pyspark.sql import functions as sf
import json
from datetime import datetime
from pyspark.ml import Pipeline
from pyspark.ml.linalg import Vectors
from pyspark.ml.feature import FeatureHasher
from pyspark.ml.classification import RandomForestClassifier
from pyspark.ml.feature import *
from pyspark.ml.evaluation import MulticlassClassificationEvaluator
from pyspark.ml.evaluation import BinaryClassificationEvaluator
from pyspark.ml.tuning import CrossValidator, ParamGridBuilder
from pyspark.sql import Row
from pyspark.sql.functions import *
from pyspark.sql.types import *
import os


spark = SparkSession \
    .builder \
    .appName("credit_train") \
    .getOrCreate()

sc = spark.sparkContext

log4jLogger = sc._jvm.org.apache.log4j 
logger = log4jLogger.LogManager.getLogger(__name__) 
logger.info("Start training")

print("ls", os.listdir())
print("ls", os.listdir("/"))
print("/data", os.listdir("/opt/spark/data"))

print("ls", SparkFiles.get("application_train.csv"))

#application_train.csv
non_feature_columns = ["SK_ID_CURR", "label", "SK_ID_PREV"]
df_train = spark.read.csv("/opt/spark/data/data/application_train.csv", inferSchema="true", header="true").cache()
df_prev_app = spark.read.csv("/opt/spark/data/data/previous_application.csv",inferSchema="true", header="true").cache()
df_payment = spark.read.csv("/opt/spark/data/data/installments_payments.csv",inferSchema="true", header="true").cache()

df_train = df_train.withColumnRenamed('TARGET','label')


# drop columns with too many null values
to_be_dropped = []

for column in [col for col in df_train.columns if col not in non_feature_columns]:
  nan_count = df_train.filter(df_train[column].isNull()).count()
  nan_ratio = nan_count / df_train.count()
  if nan_ratio > 0.4:
    to_be_dropped.append(column)

logger.info(f"Dropped {len(to_be_dropped)}")
df_train = df_train.drop(*to_be_dropped).cache()

# drop columns with too many null values
to_be_dropped = []

for column in [col for col in df_prev_app.columns if col not in non_feature_columns]:
  nan_count = df_prev_app.filter(df_prev_app[column].isNull()).count()
  nan_ratio = nan_count / df_prev_app.count()
  if nan_ratio > 0.4:
    to_be_dropped.append(column)

logger.info(f"Dropped {len(to_be_dropped)}")
df_prev_app = df_prev_app.drop(*to_be_dropped).cache()

# df_train = df_train.limit(5000).cache()

# Loan duration
df_train = df_train.withColumn("LOAN_DURATION", df_train["AMT_CREDIT"] / df_train["AMT_ANNUITY"]).cache()
df_prev_app = df_prev_app.withColumn("LOAN_DURATION", df_prev_app["AMT_CREDIT"] / df_prev_app["AMT_ANNUITY"]).cache()
# Since one application can have multiple previous applications
# We need to aggerate the previous application dataframe first
df_prev_app_means = df_prev_app.groupBy("SK_ID_CURR").mean("LOAN_DURATION", "AMT_ANNUITY", "AMT_APPLICATION", "AMT_CREDIT", "AMT_GOODS_PRICE", "DAYS_DECISION", "CNT_PAYMENT").cache()
df_payment_means = df_payment.groupBy("SK_ID_CURR").mean("DAYS_INSTALMENT", "DAYS_ENTRY_PAYMENT", "AMT_INSTALMENT", "AMT_PAYMENT").cache()
# joining to the master table
df_train = df_train.join(df_prev_app_means, ['SK_ID_CURR'], how='left').cache()
df_train = df_train.join(df_payment_means, ['SK_ID_CURR'], how='left').cache()
# filling nan values
df_train = df_train.na.fill(0).cache()

logger.info("# Rows:" + str(df_train.count()))
logger.info("# Cols:" + str(len(df_train.columns)))
labelIndexer = StringIndexer(inputCol="label", outputCol="indexedLabel").fit(df_train)
labeled = labelIndexer.transform(df_train)
hasher = FeatureHasher(inputCols=
                       [column for column in list(set(df_train.columns)) if column !='label'],
                       outputCol="indexedFeatures",
                       numFeatures=len([column for column in list(set(df_train.columns)) if column !='label']))
featurized = hasher.transform(df_train)

# Split the data into training and test sets (30% held out for testing)
trainingData, testData = df_train.randomSplit([0.7, 0.3],seed = 1234)

# Train a RandomForest model.
rf = RandomForestClassifier(labelCol="indexedLabel", featuresCol="indexedFeatures", numTrees=20, maxDepth=15)

# Chain indexers and forest in a Pipeline
pipeline = Pipeline(stages=[labelIndexer, hasher, rf])

model = pipeline.fit(trainingData)

predictions = model.transform(testData).cache()

predictions.select("prediction", "rawPrediction", "probability", "indexedLabel").show(5)

evaluator = BinaryClassificationEvaluator(
    labelCol="indexedLabel", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
auc = evaluator.evaluate(predictions)
predictions_rf = predictions

logger.info("RandomForestClassifier AUC:" +str(auc))


from pyspark.ml.classification import LogisticRegression

lr = LogisticRegression(labelCol="indexedLabel", featuresCol="indexedFeatures",maxIter=5, regParam=0.03)
pipeline = Pipeline(stages=[labelIndexer, hasher, lr])
lrModel = pipeline.fit(trainingData)
predictions = lrModel.transform(testData).cache()

evaluator = BinaryClassificationEvaluator(
    labelCol="indexedLabel", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
auc = evaluator.evaluate(predictions)
predictions_lr = predictions
logger.info("LogisticRegression AUC:" +str(auc))

from pyspark.ml.classification import GBTClassifier

gbt = GBTClassifier(labelCol="indexedLabel", featuresCol="indexedFeatures", maxIter=10, maxDepth=5)
pipeline = Pipeline(stages=[labelIndexer, hasher, gbt])
model = pipeline.fit(trainingData)
predictions = model.transform(testData).cache()

evaluator = BinaryClassificationEvaluator(
    labelCol="indexedLabel", rawPredictionCol="rawPrediction", metricName="areaUnderROC")
auc = evaluator.evaluate(predictions)
predictions_gbt = predictions
logger.info("GBTClassifier AUC:" +str(auc))


w_0 = [1/3,1/3,1/3]
w_1 = [0.2, 0.2, 0.6]
w_2 = [0.6, 0.2, 0.2]
w_3 = [0.2, 0.6, 0.2]


rf_probability = predictions_rf.select("probability", "indexedLabel").rdd.zipWithIndex().map(lambda x: (x[1], (x[0].probability.values[1], x[0].indexedLabel))).cache()
lr_probability = predictions_lr.select("probability", "indexedLabel").rdd.zipWithIndex().map(lambda x: (x[1], (x[0].probability.values[1], x[0].indexedLabel))).cache()
gbt_probability = predictions_gbt.select("probability", "indexedLabel").rdd.zipWithIndex().map(lambda x: (x[1], (x[0].probability.values[1], x[0].indexedLabel))).cache()

logger.info(rf_probability.take(2))

joined = rf_probability.join(lr_probability).map(lambda x: (x[0], (x[1][0][0], x[1][1][0], x[1][0][1]))).cache()
joined = joined.join(gbt_probability).map(lambda x: (x[0], (x[1][0][0], x[1][0][1], x[1][1][0], x[1][1][1]))).cache()



def f(x):
  d = {
      "index": x[0],
      "probability": float(x[1]),
       "label": float(x[2]),
  }
  return d
    

for w in [w_0, w_1, w_2, w_3]:
  ensemble = joined.map(lambda x: (x[0], x[1][0] * w[0] + x[1][1] * w[1] + x[1][2] * w[2], x[1][3]))
  ensemble_df = ensemble.map(lambda x: Row(**f(x))).toDF()
  evaluator = BinaryClassificationEvaluator(labelCol="label", rawPredictionCol="probability", metricName="areaUnderROC")
  auc_ensemble = evaluator.evaluate(ensemble_df)
  logger.info(w)
  logger.info("auc = " +str(auc_ensemble))