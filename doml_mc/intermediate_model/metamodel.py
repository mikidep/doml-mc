from dataclasses import dataclass
from typing import Literal, Optional

from .._utils import merge_dicts

Multiplicity = tuple[Literal["0", "1"], Literal["1", "*"]]


@dataclass
class DOMLClass:
    name: str
    superclass: Optional[str]
    attributes: dict[str, "DOMLAttribute"]
    associations: dict[str, "DOMLAssociation"]


@dataclass
class DOMLAttribute:
    name: str
    type: Literal["Boolean", "Integer", "String", "GeneratorKind"]
    multiplicity: Multiplicity


@dataclass
class DOMLAssociation:
    name: str
    type: str
    multiplicity: Multiplicity


def parse_metamodel(mmdoc: dict) -> dict[str, DOMLClass]:
    def parse_class(cname: str, cdoc: dict) -> DOMLClass:
        def parse_mult(
            mults: Literal["0..1", "0..*", "1", "1..*"]
        ) -> Multiplicity:
            if mults == "0..1":
                return ("0", "1")
            elif mults == "1":
                return ("1", "1")
            elif mults == "1..*":
                return ("1", "*")
            else:
                return ("0", "*")

        def parse_attribute(aname: str, adoc: dict) -> DOMLAttribute:
            # sourcery skip: merge-comparisons
            type_: str = adoc["type"]
            assert (
                type_ == "Boolean"
                or type_ == "Integer"
                or type_ == "String"
                or type_ == "GeneratorKind"
            )
            mults: str = adoc.get("multiplicity", "0..*")
            assert (
                mults == "0..1"
                or mults == "0..*"
                or mults == "1"
                or mults == "1..*"
            )
            return DOMLAttribute(
                name=aname,
                type=type_,
                multiplicity=parse_mult(mults),
            )

        def parse_association(aname: str, adoc: dict) -> DOMLAssociation:
            # sourcery skip: merge-comparisons
            mults: str = adoc.get("multiplicity", "0..*")
            assert (
                mults == "0..1"
                or mults == "0..*"
                or mults == "1"
                or mults == "1..*"
            )
            return DOMLAssociation(
                name=aname, type=adoc["type"], multiplicity=parse_mult(mults)
            )

        return DOMLClass(
            name=cname,
            superclass=cdoc.get("superclass"),
            attributes={
                aname: parse_attribute(aname, adoc)
                for aname, adoc in cdoc.get("attributes", {}).items()
            },
            associations={
                aname: parse_association(aname, adoc)
                for aname, adoc in cdoc.get("association", {}).items()
            },
        )

    assert set(mmdoc.keys()) <= {"commons", "application", "infrastructure"}

    return merge_dicts(
        {
            f"{prefix}_{cname}": parse_class(f"{prefix}_{cname}", cdoc)
            for cname, cdoc in csdoc.items()
        }
        for prefix, csdoc in mmdoc.items()
    )
