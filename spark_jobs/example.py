

from pyspark import SparkContext, SparkConf
import random

conf = SparkConf()
sc = SparkContext(conf=conf)

log4jLogger = sc._jvm.org.apache.log4j 
logger = log4jLogger.LogManager.getLogger(__name__) 
logger.info("Hello World!")

NUM_SAMPLES = 10000000

logger.info(f"NUM_SAMPLES {NUM_SAMPLES}")

def inside(p):
    x, y = random.random(), random.random()
    return x*x + y*y < 1

count = sc.parallelize(range(0, NUM_SAMPLES)) \
             .filter(inside).count()
logger.info("Pi is roughly %f" % (4.0 * count / NUM_SAMPLES))

