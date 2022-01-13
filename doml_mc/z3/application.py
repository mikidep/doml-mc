from z3 import (
    BoolSort,
    DatatypeRef,
    DatatypeSortRef,
    FuncDeclRef,
    Function,
    Solver,
)

from ..model.application import Application
from .utils import (
    assert_function_tuples,
    assert_relation_tuples,
    mk_enum_sort_dict,
)


def mk_application_component_sort(
    app: Application,
) -> tuple[DatatypeSortRef, dict[str, DatatypeRef]]:
    return mk_enum_sort_dict("ApplicationComponent", list(app.children.keys()))


def mk_application_type_sort(
    app: Application,
) -> tuple[DatatypeSortRef, dict[str, DatatypeRef]]:
    # TODO: This should be a predefined list of types derived from a DOML
    # definition.
    return mk_enum_sort_dict(
        "ApplicationType", list({c.typeId for c in app.children.values()})
    )


def def_and_assert_app_type_function(
    app: Application,
    solver: Solver,
    application_component_sort: DatatypeSortRef,
    application_component: dict[str, DatatypeRef],
    application_type_sort: DatatypeSortRef,
    application_type: dict[str, DatatypeRef],
) -> FuncDeclRef:
    """
    ### Effects
    This procedure is effectful on `solver`.
    """

    app_type_f = Function(
        "app_type", application_component_sort, application_type_sort
    )
    assert_function_tuples(
        app_type_f,
        solver,
        [[c.name, c.typeId] for c in app.children.values()],
        application_component,
        application_type,
    )
    return app_type_f


def mk_application_interface_sort(
    app: Application,
) -> tuple[DatatypeSortRef, dict[str, DatatypeRef]]:
    # TODO: This should be a predefined list of types derived from a DOML
    # definition.
    return mk_enum_sort_dict(
        "ApplicationInterface",
        list({i for c in app.children.values() for i in c.exposedInterfaces}),
    )


def def_and_assert_consumes_relation(
    app: Application,
    solver: Solver,
    application_component_sort: DatatypeSortRef,
    application_component: dict[str, DatatypeRef],
    application_interface_sort: DatatypeSortRef,
    application_interface: dict[str, DatatypeRef],
) -> FuncDeclRef:
    """
    ### Effects
    This procedure is effectful on `solver`.
    """

    consumes_rel = Function(
        "consumes",
        application_component_sort,
        application_interface_sort,
        application_component_sort,
        BoolSort(),
    )
    assert_relation_tuples(
        consumes_rel,
        solver,
        [
            [c.name, i, tc]
            for c in app.children.values()
            for tc in c.consumedInterfaces
            for i in c.consumedInterfaces[tc]
        ],
        application_component,
        application_interface,
        application_component,
    )
    return consumes_rel
