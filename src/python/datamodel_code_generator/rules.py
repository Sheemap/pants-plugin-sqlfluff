from pants.backend.python.util_rules.pex import PexRequest, VenvPex, VenvPexProcess
from pants.engine.fs import CreateDigest, Directory
from pants.engine.internals.native_engine import Digest, MergeDigests, Snapshot
from pants.engine.internals.selectors import MultiGet
from pants.engine.target import GenerateSourcesRequest
from pants.engine.unions import UnionRule

from pants.engine.process import FallibleProcessResult
from pants.engine.rules import Get, collect_rules, rule
from pants.engine.target import GeneratedSources
from pants.util.logging import LogLevel
from pants.backend.python.target_types import PythonSourceField
from pants.backend.openapi.target_types import OpenApiSourceField

from os.path import splitext

from datamodel_code_generator.backend.subsystem import DataModelCodeGen


class GeneratePythonFromOpenApiRequest(GenerateSourcesRequest):
    input = OpenApiSourceField
    output = PythonSourceField


@rule(desc="Generate Python from Data Model", level=LogLevel.WARN)
async def codegen(request: GeneratePythonFromOpenApiRequest, codegen: DataModelCodeGen) -> GeneratedSources:
    source_name, _ = splitext(request.protocol_sources.files[0])
    source_dir = "/".join(source_name.split("/")[:-1])

    output_name = "datamodel-codegen/" + source_name
    output_dir = "datamodel-codegen/" + source_dir

    codegen_pex, empty_out_dir = await MultiGet(
        Get(VenvPex,PexRequest, codegen.to_pex_request()), Get(Digest, CreateDigest([Directory(output_dir)]))
    )

    input_digest = await Get(
        Digest, MergeDigests([request.protocol_sources.digest, empty_out_dir])
    )

    print(request.protocol_sources)
    print(request.protocol_sources.files)

    result = await Get(
        FallibleProcessResult,
        VenvPexProcess(
            codegen_pex,
            argv=(
                "--input",
                request.protocol_sources.files[0],
                "--output",
                f"{output_name}.py"
            ),
            input_digest=input_digest,
            output_directories=(output_dir,),
            description=f"Run Codegen c:",
            level=LogLevel.WARN,
        ),
    )
    snapshot = await Get(Snapshot, Digest, result.output_digest)
    return GeneratedSources(snapshot)


def rules():
    return [
        *collect_rules(),
        UnionRule(GenerateSourcesRequest, GeneratePythonFromOpenApiRequest),
    ]
