<div align="center">

# `vet`

[![Discord](https://badgen.net/badge/icon/discord?icon=nope&label&color=purple)](https://discord.gg/caeTPJDMZj)

A poetry plugin for establishing chain of trust  
Inspired by [cargo-vet](https://github.com/mozilla/cargo-vet)

</div>


```
> poetry vet
...
👍 pexpect-4.9.0 matches exemption
👍 pkginfo-1.10.0 matches exemption
✅ platformdirs-4.2.0 passes our audit
✅ pluggy-1.4.0 passes our audit
✅ poetry-1.8.2 passes audit by TrustedOrg
✅ pyright-1.1.356 passes audit by OtherTrustedOrg
...
```

## Background

After details of the [xz backdoor](https://boehs.org/node/everything-i-know-about-the-xz-backdoor) came out, 
I thought we needed better visibility into our dependency trees.

This first iteration of `vet` is an MVP.
Should `vet` accrue interest, next steps are:
- [ ] Support for auditing version deltas
- [ ] CLI tools for auditing and importing audits (instead of manual editing)
- [ ] More robust testing

If you're interested in `vet`, or more generally in securing software supply chains, reach out on [Discord](https://discord.gg/caeTPJDMZj).

## Installation

Depending on how you installed poetry, you may need to install `vet` in a different way.

If you used the self-installer:
    
```bash
poetry self add vet
```

If you used pipx:

```bash
pipx inject poetry vet
```

If you used pip:

```bash
pip install vet
```

For more information and troubleshooting, see the [poetry plugin installation docs](https://python-poetry.org/docs/plugins/#using-plugins).

## Usage

### Initialization

Initialize `vet` in your project:

```bash
poetry vet init
```

This will create a [`chain-of-trust` directory](chain-of-trust/) in your project.
See the [generated README](chain-of-trust/README.md) for more information on how to configure `vet`.


### Running checks

To audit your project dependencies, run:

```bash
poetry vet
```

Dependencies are trusted to be either **safe to run** or **safe to deploy**. 
Upon initialization, all dependencies in the `poetry.lock` file are exempt, deemed **safe to run**.

To vet dependencies as **safe to deploy**, run:

```bash
poetry vet --safe-to-deploy
```

For an example of how to run `vet` in GitHub CI, see [the `ci.yml` file in this repository](https://github.com/irgolic/vet/blob/main/.github/workflows/ci.yml#L15).

### Importing Audits

Modify the `config.toml` file as per the example in [the generated README](chain-of-trust/README.md#imports).

Then run:

```bash
poetry vet lock
```

This will download the audits from the trusted sources specified in the `config.toml` file and store them in the `import.lock` file.

### Auditing

Audit dependencies manually by adding entries in the `audits.toml` file as per the example in [the generated README](chain-of-trust/README.md#audit-file-auditstoml).
