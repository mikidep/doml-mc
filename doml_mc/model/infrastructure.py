from dataclasses import dataclass


@dataclass
class Infrastructure:
    nodes: dict[str, "InfrastructureNode"]
    networks: dict[str, "Network"]
    groups: dict[str, "Group"]


def parse_infrastructure(doc: dict) -> Infrastructure:
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


@dataclass
class InfrastructureNode:
    name: str
    typeId: str


def parse_infrastructure_node(doc: dict) -> InfrastructureNode:
    return InfrastructureNode(
        name=doc["name"],
        typeId=doc["typeId"],
    )


@dataclass
class Network:
    name: str
    protocol: str
    addressRange: str


def parse_network(doc: dict) -> Network:
    return Network(
        name=doc["name"],
        protocol=doc["protocol"],
        addressRange=doc["addressRange"],
    )


@dataclass
class Group:
    name: str
    typeId: str


def parse_group(doc: dict) -> Group:
    return Group(
        name=doc["name"],
        typeId=doc["typeId"],
    )
