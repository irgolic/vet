def test_load_config(commands):
    commands._load_config_file()


def test_load_audits(commands):
    commands._load_audit_file()


def test_load_imports_lock(commands):
    commands._load_import_lock_file()


def test_check(commands):
    commands.check(check_safe_to_deploy=False)
