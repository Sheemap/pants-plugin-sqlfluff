from typing import ClassVar

from pants.engine.target import (COMMON_TARGET_FIELDS, SingleSourceField,
                                 StringField, Target)


class SqlSourceField(SingleSourceField):
    expected_file_extensions: ClassVar[tuple[str, ...]] = ("", ".sql")


class SqlDialectField(StringField):
    alias = "dialect"
    valid_choices = (
        "ansi",
        "athena",
        "bigquery",
        "clickhouse",
        "databricks",
        "db2",
        "duckdb",
        "exasol",
        "greenplum",
        "hive",
        "materialize",
        "mysql",
        "oracle",
        "postgres",
        "redshift",
        "snowflake",
        "soql",
        "sparksql",
        "sqlite",
        "teradata",
        "tsql",
        "vertica",
    )


class SqlSourceTarget(Target):
    alias = "sql_source"
    core_fields = (
        *COMMON_TARGET_FIELDS,
        SqlSourceField,
        SqlDialectField,
    )
    help = "A single SQL source file."
