from vet.models.config import Import


def test_init_and_check(dummy_commands):
    dummy_commands.init()
    dummy_commands.check(check_safe_to_deploy=False)


def test_lock(dummy_commands, dummy_repo):
    dummy_commands.init()

    assert dummy_commands._load_import_lock_file().audits == {}

    config = dummy_commands._load_config_file()
    config.imports["dummy"] = Import(
        url="https://raw.githubusercontent.com/irgolic/vet/main/chain-of-trust/audits.toml"
    )
    dummy_commands._save_config_file(config)
    dummy_commands.lock()

    assert dummy_commands._load_import_lock_file().audits != {}
