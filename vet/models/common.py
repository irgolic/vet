import typing

import msgspec
from packaging.utils import NormalizedName

PackageName = typing.NewType("PackageName", NormalizedName)
OrganizationName = typing.NewType("OrganizationName", NormalizedName)


class StrictStruct(
    msgspec.Struct,
    forbid_unknown_fields=True,
):
    pass


Decodable = str | bytes


def load_toml_file(data: Decodable, cls: type):
    return msgspec.toml.decode(data, type=cls)
