from typing import cast

from pants.backend.python.subsystems.setup import PythonSetup
from pants.backend.python.util_rules import pex
from pants.backend.python.util_rules.interpreter_constraints import (
    InterpreterConstraints,
)
from pants.backend.python.util_rules.pex import PexRequest, VenvPex, VenvPexProcess
from pants.core.goals.fmt import FmtResult, FmtTargetsRequest
from pants.core.util_rules.partitions import Partition, Partitions
from pants.engine.fs import Digest, MergeDigests
from pants.engine.process import FallibleProcessResult
from pants.engine.rules import Get, collect_rules, rule
from pants.util.logging import LogLevel
from pants.util.strutil import pluralize, softwrap
from sqlfluff.backend.subsystem import SqlFluff, SqlFluffFieldSet


class SqlFluffRequest(FmtTargetsRequest):
    field_set_type = SqlFluffFieldSet
    tool_subsystem = SqlFluff


async def _run_sqlfluff(
    request: SqlFluffRequest.Batch,
    sqlfluff: SqlFluff,
    metadata: tuple[str, InterpreterConstraints],
) -> FmtResult:
    pex_get = Get(
        VenvPex,
        PexRequest,
        sqlfluff.to_pex_request(interpreter_constraints=metadata[1]),
    )

    sqlfluff_pex = await pex_get

    input_digest = await Get(Digest, MergeDigests((request.snapshot.digest,)))

    result = await Get(
        FallibleProcessResult,
        VenvPexProcess(
            sqlfluff_pex,
            argv=(
                "format",
                # *(("--config", sqlfluff.config) if black.config else ()),
                "-d",
                metadata[0],
                "-p",
                "{pants_concurrency}",
                *sqlfluff.args,
                *request.files,
            ),
            input_digest=input_digest,
            output_files=request.files,
            concurrency_available=len(request.files),
            description=f"Run SQLFluff on {pluralize(len(request.files), 'file')}.",
            level=LogLevel.DEBUG,
        ),
    )

    return await FmtResult.create(request, result)


@rule
async def partition_sqlfluff(
    request: SqlFluffRequest.PartitionRequest,
    sqlfluff: SqlFluff,
    python_setup: PythonSetup,
) -> Partitions:
    if sqlfluff.skip:
        return Partitions()

    partitioned_by_dialect = {}
    for f in request.field_sets:
        if f.dialect.value not in partitioned_by_dialect:
            partitioned_by_dialect[f.dialect.value] = []

        partitioned_by_dialect[f.dialect.value].append(f)

    # Black requires 3.6+ but uses the typed-ast library to work with 2.7, 3.4, 3.5, 3.6, and 3.7.
    # However, typed-ast does not understand 3.8+, so instead we must run Black with Python 3.8+
    # when relevant. We only do this if <3.8 can't be used, as we don't want a loose requirement
    # like `>=3.6` to result in requiring Python 3.8, which would error if 3.8 is not installed on
    # the machine.
    tool_interpreter_constraints = sqlfluff.interpreter_constraints
    if sqlfluff.options.is_default("interpreter_constraints"):
        try:
            # Don't compute this unless we have to, since it might fail.
            all_interpreter_constraints = (
                InterpreterConstraints.create_from_compatibility_fields(
                    (
                        field_set.interpreter_constraints
                        for field_set in request.field_sets
                    ),
                    python_setup,
                )
            )
        except ValueError:
            raise ValueError(
                softwrap(
                    """
                    Could not compute an interpreter to run SQLFluff on, due to conflicting requirements
                    in the repo.

                    Please set `[sqlfluff].interpreter_constraints` explicitly in pants.toml to a
                    suitable interpreter.
                    """
                )
            )
        if all_interpreter_constraints.requires_python38_or_newer(
            python_setup.interpreter_versions_universe
        ):
            tool_interpreter_constraints = all_interpreter_constraints

    return Partitions(
        [
            Partition(
                (field_set.source.file_path for field_set in partitioned_by_dialect[x]),
                metadata=(x, tool_interpreter_constraints),
            )
            for x in partitioned_by_dialect
        ]
    )


@rule(desc="Format with SQLFluff", level=LogLevel.DEBUG)
async def sqlfluff_fmt(request: SqlFluffRequest.Batch, sqlfluff: SqlFluff) -> FmtResult:
    return await _run_sqlfluff(
        request, sqlfluff, cast(InterpreterConstraints, request.partition_metadata)
    )


def rules():
    return [
        *collect_rules(),
        *SqlFluffRequest.rules(),
        *pex.rules(),
    ]
