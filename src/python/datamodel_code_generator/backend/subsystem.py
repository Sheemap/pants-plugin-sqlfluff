from dataclasses import dataclass

from pants.backend.python.subsystems.python_tool_base import PythonToolBase
from pants.backend.python.target_types import ConsoleScript, InterpreterConstraintsField
from pants.engine.rules import collect_rules
from pants.engine.target import FieldSet
from pants.option.option_types import ArgsListOption, SkipOption


class DataModelCodeGen(PythonToolBase):
    name = "Data Model Code Generator"
    options_scope = "datamodel-code-generator"
    help = "The datamodel-code-generator (https://github.com/koxudaxi/datamodel-code-generator)"

    skip = SkipOption("codegen")
    args = ArgsListOption(example="-i 2")

    default_main = ConsoleScript("datamodel-codegen")
    default_requirements = ["datamodel-code-generator"]

    register_interpreter_constraints = True
    default_interpreter_constraints = ["CPython>=3.7,<=3.12"]

    default_lockfile_resource = (
        "datamodel_code_generator",
        "datamodel_code_generator.lock",
    )
