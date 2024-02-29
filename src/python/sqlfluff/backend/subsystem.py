from dataclasses import dataclass

from pants.backend.python.subsystems.python_tool_base import PythonToolBase
from pants.backend.python.target_types import (ConsoleScript,
                                               InterpreterConstraintsField)
from pants.engine.rules import collect_rules
from pants.engine.target import FieldSet
from pants.option.option_types import ArgsListOption, SkipOption
from sqlfluff.backend.target_types import SqlDialectField, SqlSourceField


@dataclass(frozen=True)
class SqlFluffFieldSet(FieldSet):
    required_fields = (SqlSourceField, SqlDialectField)

    source: SqlSourceField
    dialect: SqlDialectField
    interpreter_constraints: InterpreterConstraintsField


class SqlFluff(PythonToolBase):
    name = "SQLFluff"
    options_scope = "sqlfluff"
    help = "The SQLFluff SQL code formatter (https://sqlfluff.com/)."

    skip = SkipOption("fmt", "lint")
    args = ArgsListOption(example="-i 2")

    default_main = ConsoleScript("sqlfluff")
    default_requirements = ["sqlfluff"]

    register_interpreter_constraints = True
    default_interpreter_constraints = ["CPython>=3.7,<=3.12"]

    default_lockfile_resource = (
        "sqlfluff",
        "sqlfluff.lock",
    )


def rules():
    return collect_rules()
