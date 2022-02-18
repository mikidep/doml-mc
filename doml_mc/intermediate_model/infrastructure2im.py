from ipaddress import ip_address, ip_network

from ..model.infrastructure import (
    Infrastructure,
    InfrastructureNode,
    Network,
    Group,
)
from .doml_element import DOMLElement
from .._utils import merge_dicts


def infrastructure_to_im(infra: Infrastructure) -> dict[str, DOMLElement]:
    def _infra_node_to_im(
        infra_node: InfrastructureNode,
    ) -> dict[str, DOMLElement]:
        node_elem = DOMLElement(
            name=infra_node.name,
            type=infra_node.typeId,
            attributes={},
            associations={
                "infrastructure_ComputingNode::ifaces": set(
                    infra_node.network_interfaces.keys()
                )
            },
        )
        niface_elems = {
            nifacen: DOMLElement(
                name=nifacen,
                type="infrastructure_NetworkInterface",
                attributes={
                    "infrastructure_NetworkInterface::endPoint": int(
                        ip_address(niface.endPoint)
                    )
                },
                associations={
                    "infrastructure_NetworkInterface::belongsTo": {
                        niface.belongsTo
                    }
                },
            )
            for nifacen, niface in infra_node.network_interfaces.items()
        }
        return {node_elem.name: node_elem} | niface_elems

    def _network_to_im(net: Network) -> dict[str, DOMLElement]:
        return {
            net.name: DOMLElement(
                name=net.name,
                type="infrastructure_Network",
                attributes={
                    "infrastructure_Network::address_lb": int(
                        ip_network(net.addressRange)[0]
                    ),
                    "infrastructure_Network::address_ub": int(
                        ip_network(net.addressRange)[-1]
                    ),
                },
                associations={},
            )
        }

    def _group_to_im(group: Group) -> dict[str, DOMLElement]:
        return {
            group.name: DOMLElement(
                name=group.name,
                type=group.typeId,
                attributes={},
                associations={},
            )
        }

    return (
        merge_dicts(_infra_node_to_im(inode) for inode in infra.nodes.values())
        | merge_dicts(_network_to_im(net) for net in infra.networks.values())
        | merge_dicts(_group_to_im(group) for group in infra.groups.values())
    )
