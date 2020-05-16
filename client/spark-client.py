from pyspark import SparkConf, SparkContext
from pyspark.streaming import StreamingContext

from pyspark.sql import Row, SQLContext
import sys
import requests
import re


def send_df_to_dashboard(df):
    # convert mentions into array
    mentions = [str(t.mention) for t in df.select("mention").collect()]

    # convert counts of mentions into array
    mentions_counts = [t.mention_count for t in df.select("mention_count").collect()]

    # post data to dashboard
    data = {'labels': mentions, 'values': mentions_counts}
    print("Data:", data)
    requests.post('http://localhost:3000/update', json=data)


def process_rdd(rdd):
    try:
        pass
        # convert the RDD to Row RDD
        row_rdd = rdd.map(lambda w: Row(mention=w[0], mention_count=w[1]))

        # get spark sql singleton context from the current context
        if 'sqlContextSingletonInstance' not in globals():
            globals()['sqlContextSingletonInstance'] = SQLContext(rdd.context)
        sql_context = globals()['sqlContextSingletonInstance']

        # create a data frame from the Row RDD
        mentions_df = sql_context.createDataFrame(row_rdd)

        # register the data frame as table
        mentions_df.registerTempTable("mentions")

        # get the top 10 mentions from the table
        top_mentions = sql_context.sql("select * from mentions order by mention_count desc limit 10")
        top_mentions.show()

        # send top mentions
        send_df_to_dashboard(top_mentions)
    except:
        e = sys.exc_info()[0]
        print("Error: %s" % e)


def merge_batches(new_values, total_sum):
    return sum(new_values) + (total_sum or 0)


def main():
    # create spark configuration
    conf = SparkConf()
    conf.setAppName("twitter_streaming")

    # create spark context with the above configuration
    sc = SparkContext(conf=conf)
    sc.setLogLevel("ERROR")

    # Streaming Context is the main entry point for all streaming functionality
    # it is created from the above spark context with interval size 3 seconds
    ssc = StreamingContext(sc, 3)

    # setting a checkpoint to allow RDD recovery
    ssc.checkpoint("checkpoint")

    # Spark Streaming provides a high-level abstraction called DStream, which represents a continuous stream of data.
    # In our case DStreams are created from TCP socket streams.
    # Internally, a DStream is represented as a sequence of RDDs.
    # On each batch interval one RDD is produced independent of number of records.
    tweets = ssc.socketTextStream("localhost", 9000)

    # split each tweet by space into words
    # flatMap() is a one-to-many DStream operation that creates a new DStream
    # by generating multiple new records from each record in the source DStream.
    words = tweets.flatMap(lambda tweet: re.split('[.,? ]', tweet))

    '''
    # Count each word in each batch
    # map() is a one-to-one transformation
    pairs = words.map(lambda word: (word, 1))
    word_counts = pairs.reduceByKey(lambda x, y: x + y)

    # Print the first ten elements of each RDD generated in this DStream to the console
    word_counts.pprint()
    '''

    # filter the words to get only mentions (with @ character and not ':', since "RT @user:" is a retweet)
    # map each mention to be a tuple (mention,1)
    # mentions = words.filter(lambda w: '@' in w) \
    mentions = words.filter(lambda word: '@' in word and ':' not in word) \
        .map(lambda mention: (mention, 1)) \
        .reduceByKey(lambda x, y: x + y) \
        .updateStateByKey(merge_batches)

    # do processing for each RDD generated in each interval
    mentions.foreachRDD(process_rdd)

    # start the streaming computation
    ssc.start()

    # wait for the streaming to finish
    ssc.awaitTermination()


if __name__ == '__main__':
    main()
