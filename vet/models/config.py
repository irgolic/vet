from poetry.core.constraints.version import VersionConstraint, parse_constraint

from vet.models.audits import AuditStatus
from vet.models.common import (
    StrictStruct,
    load_toml_file,
    PackageName,
    Decodable,
    OrganizationName,
)


class Import(StrictStruct):
    """Import someone else's audits file"""

    url: str


class Exemption(StrictStruct):
    """Exempt a package from audits"""

    version: str
    status: AuditStatus

    def parse_version(self) -> VersionConstraint:
        return parse_constraint(self.version)


class TopLevelConfig(StrictStruct):
    imports: dict[OrganizationName, Import] = {}
    exemptions: dict[PackageName, Exemption] = {}

    @classmethod
    def load(cls, data: Decodable) -> "TopLevelConfig":
        config = load_toml_file(data, cls)
        for package_name, exemption in config.exemptions.items():
            exemption.parse_version()
        return config
