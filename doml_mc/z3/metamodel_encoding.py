from z3 import (
    And,
    BoolSort,
    Const,
    Consts,
    DatatypeSortRef,
    Exists,
    ForAll,
    FuncDeclRef,
    Function,
    Implies,
    Or,
    Solver,
)
from ..intermediate_model.types import MetaModel
from ..intermediate_model.metamodel import get_subclasses_dict

from .types import Refs, SortAndRefs
from .utils import mk_enum_sort_dict


def mk_class_sort_dict(
    mm: MetaModel,
) -> SortAndRefs:
    return mk_enum_sort_dict("Class", list(mm))


def mk_attribute_sort_dict(
    mm: MetaModel,
) -> SortAndRefs:
    atts = [
        f"{cname}::{aname}"
        for cname, c in mm.items()
        for aname in c.attributes
    ]
    return mk_enum_sort_dict("Attribute", atts)


def mk_association_sort_dict(
    mm: MetaModel,
) -> SortAndRefs:
    assocs = [
        f"{cname}::{aname}"
        for cname, c in mm.items()
        for aname in c.associations
    ]
    return mk_enum_sort_dict("Association", assocs)


def def_attribute_rel_and_assert_types(
    mm: MetaModel,
    solver: Solver,
    attr_sort: DatatypeSortRef,
    attr: Refs,
    class_: Refs,
    elem_class_f: FuncDeclRef,
    elem_sort: DatatypeSortRef,
    AData: DatatypeSortRef,
    ss: Refs,
) -> FuncDeclRef:
    """
    ### Effects
    This procedure is effectful on `solver`.
    """
    attr_rel = Function("attribute", elem_sort, attr_sort, AData, BoolSort())
    subclasses_dict = get_subclasses_dict(mm)
    es = Const("es", elem_sort)
    ad, ad_ = Consts("ad ad_", AData)
    # A type validity constraint is added for every attribute:
    for cname, c in mm.items():
        src_subclass_cond = Or(  # Source subclass condition
            *(
                elem_class_f(es) == class_[scname]
                for scname in subclasses_dict[cname]
            )
        )
        for mm_attr in c.attributes.values():
            # For all source elements and attribute data, their classes must be
            # a subtype of the source class, and the data must be of the data
            # type of the attribute.
            if mm_attr.type == "Boolean":
                tgt_type_cond = AData.is_bool(ad)  # type: ignore
            elif mm_attr.type == "Integer":
                tgt_type_cond = AData.is_int(ad)  # type: ignore
            elif mm_attr.type == "String":
                tgt_type_cond = AData.is_ss(ad)  # type: ignore
            else:  # mm_attr.type == "GeneratorKind"
                tgt_type_cond = Or(
                    ad == AData.ss(ss["IMAGE"]),  # type: ignore
                    ad == AData.ss(ss["SCRIPT"]),  # type: ignore
                )
            assn = ForAll(
                [es, ad],
                Implies(
                    attr_rel(es, attr[f"{cname}::{mm_attr.name}"], ad),
                    And(
                        src_subclass_cond,
                        tgt_type_cond,
                    ),
                ),
            )
            solver.assert_and_track(
                assn, f"attribute_st_types {cname}::{mm_attr.name}"
            )

            # Multiplicity constraints
            lb, ub = mm_attr.multiplicity
            if lb == "1":
                mult_lb_assn = ForAll(
                    [es],
                    Implies(
                        src_subclass_cond,
                        Exists(
                            [ad],
                            attr_rel(es, attr[f"{cname}::{mm_attr.name}"], ad),
                        ),
                    ),
                )
                solver.assert_and_track(
                    mult_lb_assn,
                    f"attribute_mult_lb {cname}::{mm_attr.name}",
                )
            if ub == "1":
                mult_ub_assn = ForAll(
                    [es, ad, ad_],
                    Implies(
                        And(
                            attr_rel(es, attr[f"{cname}::{mm_attr.name}"], ad),
                            attr_rel(
                                es, attr[f"{cname}::{mm_attr.name}"], ad_
                            ),
                        ),
                        ad == ad_,
                    ),
                )
                solver.assert_and_track(
                    mult_ub_assn,
                    f"attribute_mult_ub {cname}::{mm_attr.name}",
                )
    return attr_rel


def def_association_rel_and_assert_types(
    mm: MetaModel,
    solver: Solver,
    assoc_sort: DatatypeSortRef,
    assoc: Refs,
    class_: Refs,
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
    es, et, et_ = Consts("es et et_", elem_sort)
    # A type validity constraint is added for every association:
    for cname, c in mm.items():
        src_subclass_cond = Or(  # Source subclass condition
            *(
                elem_class_f(es) == class_[scname]
                for scname in subclasses_dict[cname]
            )
        )
        for mm_assoc in c.associations.values():
            # For all source and target elements that are associated, their
            # classes must be a subtype of the source and target classes resp.
            # of the association.
            type_assn = ForAll(
                [es, et],
                Implies(
                    assoc_rel(es, assoc[f"{cname}::{mm_assoc.name}"], et),
                    And(
                        src_subclass_cond,
                        Or(  # Target subclass condition
                            *(
                                elem_class_f(et) == class_[scname]
                                for scname in subclasses_dict[mm_assoc.type]
                            )
                        ),
                    ),
                ),
            )
            solver.assert_and_track(
                type_assn, f"association_st_types {cname}::{mm_assoc.name}"
            )

            # Multiplicity constraints
            lb, ub = mm_assoc.multiplicity
            if lb == "1":
                mult_lb_assn = ForAll(
                    [es],
                    Implies(
                        src_subclass_cond,
                        Exists(
                            [et],
                            assoc_rel(
                                es, assoc[f"{cname}::{mm_assoc.name}"], et
                            ),
                        ),
                    ),
                )
                solver.assert_and_track(
                    mult_lb_assn,
                    f"association_mult_lb {cname}::{mm_assoc.name}",
                )
            if ub == "1":
                mult_ub_assn = ForAll(
                    [es, et, et_],
                    Implies(
                        And(
                            assoc_rel(
                                es, assoc[f"{cname}::{mm_assoc.name}"], et
                            ),
                            assoc_rel(
                                es, assoc[f"{cname}::{mm_assoc.name}"], et_
                            ),
                        ),
                        et == et_,
                    ),
                )
                solver.assert_and_track(
                    mult_ub_assn,
                    f"association_mult_ub {cname}::{mm_assoc.name}",
                )
    return assoc_rel
