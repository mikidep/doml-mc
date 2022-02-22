from typing import cast
from collections.abc import Sequence
from itertools import product

from z3 import (
    BoolSort,
    BoolVal,
    Datatype,
    DatatypeSortRef,
    ExprRef,
    EnumSort,
    FuncDeclRef,
    IntSort,
    Solver,
)

from .types import Refs, SortAndRefs


def mk_enum_sort_dict(name: str, values: list[str]) -> SortAndRefs:
    """Makes a Z3 sort and a dict indexing sort values by their name"""

    sort, dtrefs = EnumSort(name, values)
    return sort, dict(zip(values, dtrefs))


def assert_relation_tuples(
    rel: FuncDeclRef,
    solver: Solver,
    rel_tpls: list[list[str]],
    *sig_dicts: Refs,
) -> None:
    """
    ### Parameters
     - `rel` is a Z3 function with return type Bool representing a relation;
     - `solver` is the Z3 solver on which to assert;
     - `rel_tpls` is a list of lists of names of symbols which are related in
       `rel`;
     - `sig_dicts` are the domains of `rel`.

    ### Effects
    This procedure is effectful on `solver`.
    """

    # Length of tuples must me homogeneous and equal to the number of given
    # domains.
    if lengths := [len(tpl) for tpl in rel_tpls]:
        assert min(lengths) == max(lengths)
        assert lengths[0] == len(sig_dicts)

    sym_tpls = [
        cast(
            list[ExprRef],
            [dom[sym_name] for sym_name, dom in zip(doms_tpl, sig_dicts)],
        )
        + [BoolVal(doms_tpl in rel_tpls)]
        for doms_tpl in map(list, product(*sig_dicts))
    ]

    assert_function_tuples_raw(rel, solver, sym_tpls)


def assert_function_tuples(
    f: FuncDeclRef,
    solver: Solver,
    f_tpls: list[list[str]],
    *sig_dicts: Refs,
) -> None:
    """
    ### Parameters
     - `f` is a Z3 function;
     - `solver` is the Z3 solver on which to assert;
     - `f_tpls` is a list of tuples of Z3 symbols. The first elements in each
       tuple are the inputs of `f`, and the last element is its output;
     - `sig_dicts` are the domains of `f`, the last one being its codomain.

    ### Effects
    This procedure is effectful on `solver`.
    """

    # Length of tuples must me homogeneous and equal to the number of given
    # domains.
    if lengths := [len(tpl) for tpl in f_tpls]:
        assert min(lengths) == max(lengths)
        assert lengths[0] == len(sig_dicts)

    sym_tpls = [
        [dom[sym_name] for sym_name, dom in zip(f_tpl, sig_dicts)]
        for f_tpl in f_tpls
    ]

    assert_function_tuples_raw(f, solver, sym_tpls)


def assert_function_tuples_raw(
    f: FuncDeclRef,
    solver: Solver,
    f_tpls: Sequence[Sequence[ExprRef]],
) -> None:
    """
    ### Parameters
     - `f` is a Z3 function;
     - `solver` is the Z3 solver on which to assert;
     - `f_tpls` is a list of tuples of Z3 references or otherwise accepted
       values. The first elements in each tuple are the inputs of `f`, and the
       last element is its output;

    ### Effects
    This procedure is effectful on `solver`.
    """
    # Length of tuples must me homogeneous.
    if lengths := [len(tpl) for tpl in f_tpls]:
        assert min(lengths) == max(lengths)

    for *xs, y in f_tpls:
        solver.append(f(*xs) == y)


def mk_stringsym_sort_from_strings(
    strings: list[str],
) -> SortAndRefs:
    def symbolize(s: str) -> str:
        return "".join([c.lower() if c.isalnum() else "_" for c in s[:16]])

    ss_list = [f"ss_{i}_{symbolize(s)}" for i, s in enumerate(strings)]
    stringsym_sort, ss_refs_dict = mk_enum_sort_dict("StringSym", ss_list)
    stringsym_sort_dict = {
        s: ss_refs_dict[ss] for s, ss in zip(strings, ss_list)
    }
    return stringsym_sort, stringsym_sort_dict


def mk_adata_sort(
    ss_sort: DatatypeSortRef,
) -> DatatypeSortRef:
    AData = Datatype("AttributeData")
    AData.declare("int", ("get_int", IntSort()))
    AData.declare("bool", ("get_bool", BoolSort()))
    AData.declare("ss", ("get_ss", ss_sort))
    return AData.create()


def Iff(a, b):
    return a == b
