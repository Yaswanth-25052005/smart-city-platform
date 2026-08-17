import sys
import logging

from backend.spark.spark_session import get_spark_session
from backend.spark.loader import load_sensor_data
from backend.spark.cleaning import clean_data
from backend.spark.transformations import apply_transformations
from backend.spark.aggregations import aggregate_metrics
from backend.spark.writer import write_analytics

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SparkPipeline")

def run_pipeline():
    logger.info("Initializing Spark Session...")
    spark = get_spark_session()
    
    try:
        logger.info("Loading sensor data from MongoDB...")
        raw_df = load_sensor_data(spark)
        
        # Action to evaluate count
        raw_count = raw_df.count()
        logger.info(f"Raw records loaded: {raw_count}")
        
        if raw_count == 0:
            logger.info("No data found to process. Exiting.")
            return

        logger.info("Cleaning data...")
        cleaned_df = clean_data(raw_df)
        cleaned_count = cleaned_df.count()
        
        logger.info(f"Cleaned records: {cleaned_count}")
        logger.info(f"Invalid/Duplicate records removed: {raw_count - cleaned_count}")
        
        if cleaned_count == 0:
            logger.info("No valid data remaining after cleaning. Exiting.")
            return

        logger.info("Applying transformations...")
        transformed_df = apply_transformations(cleaned_df)
        
        logger.info("Aggregating metrics...")
        analytics_df = aggregate_metrics(transformed_df)
        
        analytics_count = analytics_df.count()
        logger.info(f"Generated {analytics_count} analytics records.")
        
        logger.info("Writing results to MongoDB...")
        write_analytics(analytics_df)
        
        logger.info("Spark pipeline execution completed successfully.")
        
    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise
    finally:
        spark.stop()

if __name__ == "__main__":
    run_pipeline()
