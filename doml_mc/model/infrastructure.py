from dataclasses import dataclass


@dataclass
class Infrastructure:
    nodes: dict[str, "InfrastructureNode"]
    networks: dict[str, "Network"]
    groups: dict[str, "Group"]


@dataclass
class InfrastructureNode:
    name: str
    typeId: str
    network_interfaces: dict[str, "NetworkInterface"]


@dataclass
class Network:
    name: str
    protocol: str
    addressRange: str


@dataclass
class NetworkInterface:
    name: str
    belongsTo: str
    endPoint: str


@dataclass
class Group:
    name: str
    typeId: str


def parse_infrastructure(doc: dict) -> Infrastructure:
    def parse_infrastructure_node(doc: dict) -> InfrastructureNode:
        def parse_network_interface(doc: dict) -> NetworkInterface:
            return NetworkInterface(
                name=doc["name"],
                belongsTo=doc["belongsTo"],
                endPoint=doc["endPoint"],
            )

        return InfrastructureNode(
            name=doc["name"],
            typeId=doc["typeId"],
            network_interfaces={
                niface_doc["name"]: parse_network_interface(niface_doc)
                for niface_doc in doc.get("interfaces", [])
            },
        )

    def parse_network(doc: dict) -> Network:
        return Network(
            name=doc["name"],
            protocol=doc["protocol"],
            addressRange=doc["addressRange"],
        )

    def parse_group(doc: dict) -> Group:
        return Group(
            name=doc["name"],
            typeId=doc["typeId"],
        )

    return Infrastructure(
        nodes={
            ndoc["name"]: parse_infrastructure_node(ndoc)
            for ndoc in doc["nodes"]
        },
        networks={
            ndoc["name"]: parse_network(ndoc) for ndoc in doc["networks"]
        },
        groups={gdoc["name"]: parse_group(gdoc) for gdoc in doc["groups"]},
    )
