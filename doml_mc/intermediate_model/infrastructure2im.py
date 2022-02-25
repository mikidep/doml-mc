from ipaddress import ip_address, ip_network

from ..model.infrastructure import (
    Infrastructure,
    InfrastructureNode,
    Network,
    Group,
)
from .._utils import merge_dicts

from .types import IntermediateModel, MetaModel
from .doml_element import DOMLElement
from .metamodel import get_subclasses_dict


def infrastructure_to_im(
    infra: Infrastructure, mm: MetaModel
) -> IntermediateModel:
    subclasses_dict = get_subclasses_dict(mm)

    def _infra_node_to_im(
        infra_node: InfrastructureNode,
    ) -> IntermediateModel:
        nifacereln = (
            "infrastructure_Storage::ifaces"
            if infra_node.typeId in subclasses_dict["infrastructure_Storage"]
            else "infrastructure_ComputingNode::ifaces"
        )
        node_elem = DOMLElement(
            name=infra_node.name,
            type=infra_node.typeId,
            attributes=infra_node.attributes
            | {"commons_DOMLElement::name": infra_node.name},
            associations=infra_node.associations
            | {nifacereln: set(infra_node.network_interfaces.keys())},
        )
        niface_elems = {
            nifacen: DOMLElement(
                name=nifacen,
                type="infrastructure_NetworkInterface",
                attributes={
                    "commons_DOMLElement::name": nifacen,
                    "infrastructure_NetworkInterface::endPoint": int(
                        ip_address(niface.endPoint)
                    ),
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

    def _network_to_im(net: Network) -> IntermediateModel:
        return {
            net.name: DOMLElement(
                name=net.name,
                type="infrastructure_Network",
                attributes={
                    "commons_DOMLElement::name": net.name,
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

    def _group_to_im(group: Group) -> IntermediateModel:
        return {
            group.name: DOMLElement(
                name=group.name,
                type=group.typeId,
                attributes={"commons_DOMLElement::name": group.name},
                associations={},
            )
        }

    return (
        merge_dicts(_infra_node_to_im(inode) for inode in infra.nodes.values())
        | merge_dicts(_network_to_im(net) for net in infra.networks.values())
        | merge_dicts(_group_to_im(group) for group in infra.groups.values())
    )
