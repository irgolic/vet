from email.utils import parseaddr
from enum import Enum

from poetry.core.constraints.version import (
    VersionConstraint,
    parse_constraint,
)

from vet.models.common import load_toml_file, StrictStruct, PackageName, Decodable


# enum
class AuditStatus(Enum):
    UNSAFE = "unsafe"
    SAFE_TO_RUN = "safe to run"
    SAFE_TO_DEPLOY = "safe to deploy"


class Audit(StrictStruct):
    who: str
    status: AuditStatus
    version: str
    notes: str = ""

    def parse_who(self) -> tuple[str, str]:
        return parseaddr(self.who)

    def parse_version(self) -> VersionConstraint:
        return parse_constraint(self.version)


class TopLevelAudits(StrictStruct):
    audits: dict[PackageName, Audit] = {}

    @classmethod
    def load(cls, data: Decodable) -> "TopLevelAudits":
        audits = load_toml_file(data, cls)
        for package_name, audit in audits.audits.items():
            audit.parse_version()
            audit.parse_who()
        return audits
