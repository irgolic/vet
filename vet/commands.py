import os
from typing_extensions import assert_never

import msgspec.toml
import requests

from poetry.core.constraints.version import Version

from vet.models.audits import TopLevelAudits, AuditStatus
from vet.models.common import PackageName, OrganizationName
from vet.models.config import Exemption, TopLevelConfig
from vet.models.imports_lock import TopLevelImportsLock
from vet.texts import (
    ReadmeText,
    ExampleAudit,
    ExemptionMatch,
    AuditMatch,
    ImportedAuditMatch,
    FailedAuditMatch,
)
from vet.utils import load_poetry_lock_packages


class Commands:
    def __init__(
        self,
        root_dir: str = ".",
        config_dir_name: str = "chain-of-trust",
        readme_file: str = "README.md",
        audit_file: str = "audits.toml",
        config_file: str = "config.toml",
        import_lock_file: str = "import.lock",
    ):
        self.config_dir = os.path.normpath(os.path.join(root_dir, config_dir_name))
        self.readme_file = readme_file
        self.audit_file = audit_file
        self.config_file = config_file
        self.import_lock_file = import_lock_file

    def _create_or_update_readme(self):
        text_model = ReadmeText(
            audit_file=self.audit_file,
            config_file=self.config_file,
            import_lock_file=self.import_lock_file,
        )
        with open(
            os.path.join(
                self.config_dir,
                self.readme_file,
            ),
            "w",
        ) as f:
            f.write(text_model.text)

    def _initialize_audit_file(self):
        text_model = ExampleAudit(
            commented=True,
        )
        with open(
            os.path.join(
                self.config_dir,
                self.audit_file,
            ),
            "w",
        ) as f:
            f.write(text_model.text)

    def _initialize_config_file(self):
        packages = load_poetry_lock_packages()

        exemptions = {
            PackageName(package.name): Exemption(
                version=package.version.text,
                status=AuditStatus.SAFE_TO_RUN,
            )
            for package in packages
        }

        config = TopLevelConfig(
            imports={},
            exemptions=exemptions,
        )

        with open(
            os.path.join(
                self.config_dir,
                self.config_file,
            ),
            "wb",
        ) as f:
            f.write(msgspec.toml.encode(config))

    def _initialize_import_lock_file(self):
        config = TopLevelImportsLock(
            audits={},
        )
        with open(
            os.path.join(
                self.config_dir,
                self.import_lock_file,
            ),
            "wb",
        ) as f:
            f.write(msgspec.toml.encode(config))

    def init(self):
        """
        Initialize vet in this project (create audit.yaml).
        """
        if os.path.exists(self.config_dir):
            raise FileExistsError("chain-of-trust directory already exists")

        # create dir
        os.mkdir(self.config_dir)

        self._create_or_update_readme()
        self._initialize_audit_file()
        self._initialize_config_file()
        self._initialize_import_lock_file()

    def _load_audit_file(self) -> TopLevelAudits:
        with open(
            os.path.join(
                self.config_dir,
                self.audit_file,
            ),
            "rb",
        ) as f:
            return TopLevelAudits.load(f.read())

    def _save_audit_file(self, audits: TopLevelAudits):
        with open(
            os.path.join(
                self.config_dir,
                self.audit_file,
            ),
            "wb",
        ) as f:
            f.write(msgspec.toml.encode(audits))

    def _load_config_file(self) -> TopLevelConfig:
        with open(
            os.path.join(
                self.config_dir,
                self.config_file,
            ),
            "rb",
        ) as f:
            return TopLevelConfig.load(f.read())

    def _save_config_file(self, config: TopLevelConfig):
        with open(
            os.path.join(
                self.config_dir,
                self.config_file,
            ),
            "wb",
        ) as f:
            f.write(msgspec.toml.encode(config))

    def _load_import_lock_file(self) -> TopLevelImportsLock:
        with open(
            os.path.join(
                self.config_dir,
                self.import_lock_file,
            ),
            "rb",
        ) as f:
            return TopLevelImportsLock.load(f.read())

    def _save_import_lock_file(self, imports: TopLevelImportsLock):
        with open(
            os.path.join(
                self.config_dir,
                self.import_lock_file,
            ),
            "wb",
        ) as f:
            f.write(msgspec.toml.encode(imports))

    def _check_safety(self, status: AuditStatus, check_safe_to_deploy: bool):
        if status == AuditStatus.SAFE_TO_DEPLOY:
            return True
        elif status == AuditStatus.SAFE_TO_RUN:
            return not check_safe_to_deploy
        elif status == AuditStatus.UNSAFE:
            return False
        else:
            assert_never(status)

    def _check_exemptions(
        self,
        config: TopLevelConfig,
        package_name: PackageName,
        version: Version,
        check_safe_to_deploy: bool,
    ) -> bool:
        if package_name in config.exemptions:
            exemption = config.exemptions[package_name]
            version_constraint = exemption.parse_version()
            if version_constraint.allows(version):
                return self._check_safety(exemption.status, check_safe_to_deploy)
        return False

    def _check_audits(
        self,
        audits: TopLevelAudits,
        package_name: PackageName,
        version: Version,
        check_safe_to_deploy: bool,
    ) -> bool:
        if package_name in audits.audits:
            audit = audits.audits[package_name]
            version_constraint = audit.parse_version()
            if version_constraint.allows(version) and self._check_safety(
                audit.status, check_safe_to_deploy
            ):
                return True
        return False

    def _check_trusted_audits(
        self,
        imports: TopLevelImportsLock,
        package_name: PackageName,
        version: Version,
        check_safe_to_deploy: bool,
    ) -> None | OrganizationName:
        for organization_name, organization_audits in imports.audits.items():
            if package_name in organization_audits:
                audit = organization_audits[package_name]
                version_constraint = audit.parse_version()
                if version_constraint.allows(version) and self._check_safety(
                    audit.status, check_safe_to_deploy
                ):
                    return organization_name
        return None

    def check(self, check_safe_to_deploy: bool):
        """
        Check the audit file against dependency versions, and exit with a non-zero status if there are any.
        """
        config = self._load_config_file()
        audits = self._load_audit_file()
        imports = self._load_import_lock_file()

        failed_audits = []

        packages = load_poetry_lock_packages()
        for package in packages:
            package_name = PackageName(package.name)
            package_version = package.version

            # check exemptions
            is_exempt = self._check_exemptions(
                config, package_name, package_version, check_safe_to_deploy
            )
            # check audits
            passes_audit = self._check_audits(
                audits, package_name, package_version, check_safe_to_deploy
            )
            if passes_audit:
                print(
                    AuditMatch(
                        package_name=package.unique_name,
                        is_exempt=is_exempt,
                    ).text
                )
                continue

            if is_exempt:
                print(ExemptionMatch(package_name=package.unique_name).text)
                continue

            # check imported audits
            auditing_org_name = self._check_trusted_audits(
                imports, package_name, package_version, check_safe_to_deploy
            )
            if auditing_org_name:
                print(
                    ImportedAuditMatch(
                        package_name=package.unique_name,
                        org_name=auditing_org_name,
                    ).text
                )
                continue

            # audit failed
            print(
                FailedAuditMatch(
                    package_name=package.unique_name,
                ).text
            )
            failed_audits.append(package)

        return failed_audits

    def lock(self):
        config = self._load_config_file()

        org_audits = {}
        for org_name, import_ in config.imports.items():
            url = import_.url
            response = requests.get(url)
            response.raise_for_status()

            audits = TopLevelAudits.load(response.content).audits
            org_audits[org_name] = audits

        imports = TopLevelImportsLock(audits=org_audits)
        self._save_import_lock_file(imports)
