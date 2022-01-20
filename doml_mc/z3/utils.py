from typing import cast
from itertools import product

from z3 import (
    DatatypeRef,
    DatatypeSortRef,
    EnumSort,
    FuncDeclRef,
    Not,
    Solver,
)


def mk_enum_sort_dict(
    name: str, values: list[str]
) -> tuple[DatatypeSortRef, dict[str, DatatypeRef]]:
    """Makes a Z3 sort and a dict indexing sort values by their name"""

    sort, dtrefs = EnumSort(name, values)
    return sort, dict(zip(values, dtrefs))


def assert_relation_tuples(
    rel: FuncDeclRef,
    solver: Solver,
    rel_tpls: list[list[str]],
    *sig_dicts: dict[str, DatatypeRef]
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
    lengths = [len(tpl) for tpl in rel_tpls]
    if lengths:
        assert min(lengths) == max(lengths)
        assert lengths[0] == len(sig_dicts)

    for doms_tpl in map(list, product(*sig_dicts)):
        doms_tpl = cast(list[str], doms_tpl)
        sym_tpl = [dom[sym_name] for sym_name, dom in zip(doms_tpl, sig_dicts)]
        if doms_tpl in rel_tpls:
            solver.append(rel(*sym_tpl))
        else:
            solver.append(Not(rel(*sym_tpl)))


def assert_function_tuples(
    f: FuncDeclRef,
    solver: Solver,
    f_tpls: list[list[str]],
    *sig_dicts: dict[str, DatatypeRef]
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
    lengths = [len(tpl) for tpl in f_tpls]
    if lengths:
        assert min(lengths) == max(lengths)
        assert lengths[0] == len(sig_dicts)

    for f_tpl in f_tpls:
        sym_tpl = [dom[sym_name] for sym_name, dom in zip(f_tpl, sig_dicts)]
        *xs, y = sym_tpl
        solver.append(f(*xs) == y)
