from ipaddress import ip_network

from z3 import (
    DatatypeRef,
    DatatypeSortRef,
    FuncDeclRef,
    Function,
    IntSort,
    Solver,
)

from ..model.infrastructure import Infrastructure
from .utils import (
    assert_function_tuples,
    mk_enum_sort_dict,
)


def mk_infrastructure_node_sort(
    infra: Infrastructure,
) -> tuple[DatatypeSortRef, dict[str, DatatypeRef]]:
    return mk_enum_sort_dict("InfrastructureNode", list(infra.nodes.keys()))


def mk_infrastructure_node_type_sort(
    infra: Infrastructure,
) -> tuple[DatatypeSortRef, dict[str, DatatypeRef]]:
    # TODO: This should be a predefined list of types derived from a DOML
    # definition.
    return mk_enum_sort_dict(
        "InfrastructureNodeType",
        list({c.typeId for c in infra.nodes.values()}),
    )


def def_and_assert_infra_node_type_function(
    infra: Infrastructure,
    solver: Solver,
    infrastructure_node_sort: DatatypeSortRef,
    infrastructure_node: dict[str, DatatypeRef],
    infrastructure_node_type_sort: DatatypeSortRef,
    infrastructure_node_type: dict[str, DatatypeRef],
) -> FuncDeclRef:
    """
    ### Effects
    This procedure is effectful on `solver`.
    """

    infra_node_type_f = Function(
        "infra_node_type",
        infrastructure_node_sort,
        infrastructure_node_type_sort,
    )
    assert_function_tuples(
        infra_node_type_f,
        solver,
        [[c.name, c.typeId] for c in infra.nodes.values()],
        infrastructure_node,
        infrastructure_node_type,
    )
    return infra_node_type_f


def mk_infrastructure_network_sort(
    infra: Infrastructure,
) -> tuple[DatatypeSortRef, dict[str, DatatypeRef]]:
    return mk_enum_sort_dict(
        "InfrastructureNetwork", list(infra.networks.keys())
    )


def mk_network_protocol_sort() -> tuple[
    DatatypeSortRef, dict[str, DatatypeRef]
]:
    return mk_enum_sort_dict(
        "NetworkProtocol",
        [
            "TCP/IP",
            "UDP",
        ],
    )


def def_and_assert_network_protocol_function(
    infra: Infrastructure,
    solver: Solver,
    infrastructure_network_sort: DatatypeSortRef,
    infrastructure_network: dict[str, DatatypeRef],
    network_protocol_sort: DatatypeSortRef,
    network_protocol: dict[str, DatatypeRef],
) -> FuncDeclRef:
    """
    ### Effects
    This procedure is effectful on `solver`.
    """

    network_proto_f = Function(
        "network_proto", infrastructure_network_sort, network_protocol_sort
    )
    assert_function_tuples(
        network_proto_f,
        solver,
        [[n.name, n.protocol] for n in infra.networks.values()],
        infrastructure_network,
        network_protocol,
    )
    return network_proto_f


def def_and_assert_network_first_address_function(
    infra: Infrastructure,
    solver: Solver,
    infrastructure_network_sort: DatatypeSortRef,
    infrastructure_network: dict[str, DatatypeRef],
) -> FuncDeclRef:
    """
    ### Effects
    This procedure is effectful on `solver`.
    """

    network_first_addr_f = Function(
        "network_first_addr", infrastructure_network_sort, IntSort()
    )
    for n in infra.networks.values():
        solver.append(
            network_first_addr_f(infrastructure_network[n.name])
            == int(ip_network(n.addressRange)[0])
        )
    return network_first_addr_f


def def_and_assert_network_last_address_function(
    infra: Infrastructure,
    solver: Solver,
    infrastructure_network_sort: DatatypeSortRef,
    infrastructure_network: dict[str, DatatypeRef],
) -> FuncDeclRef:
    """
    ### Effects
    This procedure is effectful on `solver`.
    """

    network_last_addr_f = Function(
        "network_last_addr", infrastructure_network_sort, IntSort()
    )
    for n in infra.networks.values():
        solver.append(
            network_last_addr_f(infrastructure_network[n.name])
            == int(ip_network(n.addressRange)[-1])
        )
    return network_last_addr_f


def mk_infrastructure_group_sort(
    infra: Infrastructure,
) -> tuple[DatatypeSortRef, dict[str, DatatypeRef]]:
    return mk_enum_sort_dict("InfrastructureGroup", list(infra.groups.keys()))


def mk_infrastructure_group_type_sort(
    infra: Infrastructure,
) -> tuple[DatatypeSortRef, dict[str, DatatypeRef]]:
    # TODO: This should be a predefined list of types derived from a DOML
    # definition.
    return mk_enum_sort_dict(
        "InfrastructureGroupType",
        list({g.typeId for g in infra.groups.values()}),
    )


def def_and_assert_infra_group_type_function(
    infra: Infrastructure,
    solver: Solver,
    infrastructure_group_sort: DatatypeSortRef,
    infrastructure_group: dict[str, DatatypeRef],
    infrastructure_group_type_sort: DatatypeSortRef,
    infrastructure_group_type: dict[str, DatatypeRef],
) -> FuncDeclRef:
    """
    ### Effects
    This procedure is effectful on `solver`.
    """

    infra_group_type_f = Function(
        "infra_group_type",
        infrastructure_group_sort,
        infrastructure_group_type_sort,
    )
    assert_function_tuples(
        infra_group_type_f,
        solver,
        [[g.name, g.typeId] for g in infra.groups.values()],
        infrastructure_group,
        infrastructure_group_type,
    )
    return infra_group_type_f
