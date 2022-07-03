from pyspark.sql import DataFrame, functions

from spark_pipeline.base.spark_client import CreateSession

QUERY = """
SELECT
    Id,
    Name,
    Death_year
FROM
    deaths
"""


def extract() -> DataFrame:
    """This function loads a .csv file and creates a Spark DataFrame.

    Returns:
        Spark DataFrame
    """
    CreateSession().read.load(
        "data/AgeDataset-V1.csv",
        format="csv",
        inferSchema="true",
        header="true",
    ).createOrReplaceTempView("deaths")
    return CreateSession().sql(QUERY)


def transform(df: DataFrame) -> DataFrame:
    """This function counts the IDs grouping by death year.

    Args:
        df (DataFrame): Spark DataFrame

    Returns:
        DataFrame: Aggregated DataFrame
    """
    df_blank = df.fillna("Blank", subset=["Death_year"]).select(functions.col("Id"), functions.col("Death_year").cast("int"))

    agg_df = (
        df_blank.groupBy("Death_year")
        .agg(functions.count(functions.col("Id")).alias("total_deaths"))
        .select("Death_year", "total_deaths").orderBy("Death_year")
    )
    return agg_df


def load(df: DataFrame) -> None:
    """This function recieves a aggregated DataFrame and writes as a parquet file.

    Args:
        df (DataFrame): Aggregated DataFrame
    """
    df.coalesce(1).write.parquet("data/output", mode = 'overwrite')
    return None
