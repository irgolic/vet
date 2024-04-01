from poetry.core.packages.package import Package as PoetryPackage

from poetry.factory import Factory as PoetryFactory


def load_poetry_lock_packages() -> list[PoetryPackage]:
    poetry = PoetryFactory().create_poetry()
    locker = poetry.locker
    # locker = Locker(Path("poetry.lock"), {})
    if not locker.is_locked():
        raise FileNotFoundError("poetry.lock not found")
    if not locker.is_fresh():
        raise ValueError(
            "pyproject.toml changed significantly since poetry.lock was last generated. "
            "Run `poetry lock [--no-update]` to fix the lock file."
        )

    repository = locker.locked_repository()
    return repository.packages
