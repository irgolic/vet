from vet.models.audits import Audit
from vet.models.common import (
    StrictStruct,
    OrganizationName,
    PackageName,
    load_toml_file,
    Decodable,
)


class TopLevelImportsLock(StrictStruct):
    audits: dict[OrganizationName, dict[PackageName, Audit]] = {}

    @classmethod
    def load(cls, data: Decodable) -> "TopLevelImportsLock":
        lock = load_toml_file(data, cls)
        for organization_name, audits in lock.audits.items():
            for package_name, audit in audits.items():
                audit.parse_version()
                audit.parse_who()
        return lock
