from typing import cast

import networkx as nx
from z3 import (
    And,
    BoolSort,
    Const,
    Consts,
    DatatypeRef,
    DatatypeSortRef,
    ForAll,
    FuncDeclRef,
    Function,
    Implies,
    Or,
    Solver,
)
from ..intermediate_model.metamodel import DOMLClass
from .utils import mk_enum_sort_dict


def mk_class_sort_dict(
    mm: dict[str, DOMLClass]
) -> tuple[DatatypeSortRef, dict[str, DatatypeRef]]:
    return mk_enum_sort_dict("Element", list(mm))


def mk_attribute_sort_dict(
    mm: dict[str, DOMLClass]
) -> tuple[DatatypeSortRef, dict[str, DatatypeRef]]:
    atts = [
        f"{cname}::{aname}"
        for cname, c in mm.items()
        for aname in c.attributes
    ]
    return mk_enum_sort_dict("Attribute", atts)


def mk_association_sort_dict(
    mm: dict[str, DOMLClass]
) -> tuple[DatatypeSortRef, dict[str, DatatypeRef]]:
    assocs = [
        f"{cname}::{aname}"
        for cname, c in mm.items()
        for aname in c.associations
    ]
    return mk_enum_sort_dict("Association", assocs)


def get_subclasses_dict(mm: dict[str, DOMLClass]) -> dict[str, set[str]]:
    inherits_dg = nx.DiGraph(
        [
            (c.name, c.superclass)
            for c in mm.values()
            if c.superclass is not None
        ]
    )
    inherits_dg.add_nodes_from(mm)
    inherits_dg_trans = cast(
        nx.DiGraph, nx.transitive_closure(inherits_dg, reflexive=True)
    )
    return {cname: set(inherits_dg_trans.predecessors(cname)) for cname in mm}


def def_attribute_rel_and_assert_types(
    mm: dict[str, DOMLClass],
    solver: Solver,
    attr_sort: DatatypeSortRef,
    attr: dict[str, DatatypeRef],
    class_: dict[str, DatatypeRef],
    elem_class_f: FuncDeclRef,
    elem_sort: DatatypeSortRef,
    AData: DatatypeSortRef,
) -> FuncDeclRef:
    """
    ### Effects
    This procedure is effectful on `solver`.
    """
    attr_rel = Function("attribute", elem_sort, attr_sort, AData, BoolSort())
    subclasses_dict = get_subclasses_dict(mm)
    es = Const("es", elem_sort)
    ad = Const("ad", AData)
    # A type validity constraint is added for every attribute:
    for cname, c in mm.items():
        for mm_attr in c.attributes.values():
            # For all source and target elements that are associated, their
            # classes must be a subtype of the source and target classes resp.
            # of the association.
            if mm_attr.type == "Boolean":
                ad_assn = AData.is_bool(ad)  # type: ignore
            elif mm_attr.type == "Integer":
                ad_assn = AData.is_int(ad)  # type: ignore
            elif mm_attr.type == "String":
                ad_assn = AData.is_ss(ad)  # type: ignore
            else:  # mm_attr.type == "GeneratorKind"
                ad_assn = AData.is_gen_kind(ad)  # type: ignore
            assn = ForAll(
                [es, ad],
                Implies(
                    attr_rel(es, attr[f"{cname}::{mm_attr.name}"], ad),
                    And(
                        Or(
                            *(
                                elem_class_f(es) == class_[scname]
                                for scname in subclasses_dict[cname]
                            )
                        ),
                        ad_assn,
                    ),
                ),
            )
            solver.assert_and_track(
                assn, f"attribute_st_types {cname}::{mm_attr.name}"
            )
    return attr_rel


def def_association_rel_and_assert_types(
    mm: dict[str, DOMLClass],
    solver: Solver,
    assoc_sort: DatatypeSortRef,
    assoc: dict[str, DatatypeRef],
    class_: dict[str, DatatypeRef],
    elem_class_f: FuncDeclRef,
    elem_sort: DatatypeSortRef,
) -> FuncDeclRef:
    """
    ### Effects
    This procedure is effectful on `solver`.
    """
    assoc_rel = Function(
        "association", elem_sort, assoc_sort, elem_sort, BoolSort()
    )
    subclasses_dict = get_subclasses_dict(mm)
    es, et = Consts("es et", elem_sort)
    # A type validity constraint is added for every association:
    for cname, c in mm.items():
        for mm_assoc in c.associations.values():
            # For all source and target elements that are associated, their
            # classes must be a subtype of the source and target classes resp.
            # of the association.
            assn = ForAll(
                [es, et],
                Implies(
                    assoc_rel(es, assoc[f"{cname}::{mm_assoc.name}"], et),
                    And(
                        Or(
                            *(
                                elem_class_f(es) == class_[scname]
                                for scname in subclasses_dict[cname]
                            )
                        ),
                        Or(
                            *(
                                elem_class_f(et) == class_[scname]
                                for scname in subclasses_dict[mm_assoc.type]
                            )
                        ),
                    ),
                ),
            )
            solver.assert_and_track(
                assn, f"association_st_types {cname}::{mm_assoc.name}"
            )
    return assoc_rel
