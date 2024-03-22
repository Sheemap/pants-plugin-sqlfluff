from pants.engine.addresses import Address
from pants.engine.target import Dependencies, InjectDependenciesRequest, InjectedDependencies
from pants.engine.rules import collect_rules, rule
from pants.engine.unions import UnionRule

class CodeGenDependencies(Dependencies):
    pass

class CodeGenSourceTarget(Target):
    alias = "protobuf_source"
    core_fields = (*COMMON_TARGET_FIELDS, CodeGenDependencies) #, CodeGenSourceField)

class InjectCodeGenDependencies(InjectDependenciesRequest):
    inject_for = CodeGenDependencies

@rule
async def inject_dependencies(_: InjectCodeGenDependencies) -> InjectedDependencies:
    address = Address("3rdparty/python", target_name="datamodel-code-generator")
    return InjectedDependencies([address])

def rules():
    return [
        *collect_rules(),
        UnionRule(InjectDependenciesRequest, InjectCodeGenDependencies),
    ]
