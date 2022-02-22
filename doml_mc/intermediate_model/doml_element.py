from typing import Union
from dataclasses import dataclass


@dataclass
class DOMLElement:
    name: str
    type: str
    # the keys of the `attributes`/`associations` dicts are
    # attribute/association names mangled with the type that declares them,
    # e.g., `"application_SoftwarePackage::isPersistent"`.
    attributes: dict[str, Union[str, int, bool]]
    associations: dict[str, set[str]]
