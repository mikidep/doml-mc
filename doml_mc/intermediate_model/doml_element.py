from typing import Union
from dataclasses import dataclass

from .metamodel import (
    AssociationNotFound,
    AttributeNotFound,
    MetaModel,
    get_mangled_attribute_name,
    get_mangled_association_name,
)

Attributes = dict[str, Union[str, int, bool]]
Associations = dict[str, set[str]]


@dataclass
class DOMLElement:
    name: str
    type: str
    # the keys of the `attributes`/`associations` dicts are
    # attribute/association names mangled with the type that declares them,
    # e.g., `"application_SoftwarePackage::isPersistent"`.
    attributes: Attributes
    associations: Associations


def parse_attrs_and_assocs_from_doc(
    doc: dict,
    cname: str,
    mm: MetaModel,
) -> tuple[Attributes, Associations]:
    attrs = {}
    assocs = {}
    for k, v in doc.items():
        try:
            man = get_mangled_attribute_name(mm, cname, k)
            attrs[man] = v
        except AttributeNotFound:
            try:
                man = get_mangled_association_name(mm, cname, k)
                # Only single target associations are found
                # with this function. Change otherwise.
                assocs[man] = {v}
            except AssociationNotFound:
                pass
    return attrs, assocs
