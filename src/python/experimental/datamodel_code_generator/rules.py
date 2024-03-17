from pants.backend.python.util_rules.pex import PexRequest, VenvPex, VenvPexProcess
from pants.engine.target import GenerateSourcesRequest
from pants.engine.unions import UnionRule

from pants.engine.process import FallibleProcessResult
from pants.engine.rules import Get, collect_rules, rule
from pants.engine.target import GeneratedSources
from pants.util.logging import LogLevel
from pants.backend.python.target_types import PythonSourceField
from pants.backend.openapi.target_types import OpenApiSourceField
from experimental.datamodel_code_generator.backend.subsystem import DataModelCodeGen


class GeneratePythonFromOpenApiRequest(GenerateSourcesRequest):
    input = OpenApiSourceField
    output = PythonSourceField


@rule(desc="Generate Python from Data Model", level=LogLevel.DEBUG)
async def codegen(request: GeneratePythonFromOpenApiRequest, codegen: DataModelCodeGen) -> GeneratedSources:
    codegen_pex = await Get(
        VenvPex,
        PexRequest,
        codegen.to_pex_request(),
    )

    result = await Get(
        FallibleProcessResult,
        VenvPexProcess(
            codegen_pex,
            argv=(
                "--input",
                "",
                "--ouput",
                ""
            ),
            output_files=request.files,
            concurrency_available=len(request.files),
            description=f"Run Codegen c:",
            level=LogLevel.DEBUG,
        ),
    )
    return GeneratedSources.from


def rules():
    return [
        *collect_rules(),
        UnionRule(GenerateSourcesRequest, GeneratePythonFromOpenApiRequest),
    ]
