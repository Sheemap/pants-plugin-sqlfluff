from sqlfluff.backend import rules as sqlfluff_rules
from sqlfluff.backend import subsystem
from sqlfluff.backend.target_types import SqlSourceTarget


def rules():
    return [*sqlfluff_rules.rules(), *subsystem.rules()]


def target_types():
    return [SqlSourceTarget]
