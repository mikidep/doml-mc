from dataclasses import dataclass


@dataclass
class Concretization:
    name: str
    groups: dict[str, "Group"]
    vms: dict[str, "VirtualMachine"]
    providers: dict[str, "Provider"]
    storages: dict[str, "Storage"]
    networks: dict[str, "Network"]


def parse_concretization(doc: dict) -> Concretization:
    return Concretization(
        name=doc["name"],
        groups={gdoc["name"]: parse_group(gdoc) for gdoc in doc["groups"]},
        vms={
            vmdooc["name"]: parse_virtual_machine(vmdooc)
            for vmdooc in doc["vms"]
        },
        providers={
            pdoc["name"]: parse_provider(pdoc) for pdoc in doc["providers"]
        },
        storages={
            sdoc["name"]: parse_storage(sdoc) for sdoc in doc["storages"]
        },
        networks={
            ndoc["name"]: parse_network(ndoc) for ndoc in doc["networks"]
        },
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


@dataclass
class VirtualMachine:
    name: str
    maps: str
    description: str


def parse_virtual_machine(doc: dict) -> VirtualMachine:
    return VirtualMachine(
        name=doc["name"],
        maps=doc["maps"],
        description=doc["description"],
    )


@dataclass
class Provider:
    name: str
    typeId: str
    supportedGroups: list[str]
    providedVMs: list[str]
    storages: list[str]
    providedNetworks: list[str]
    description: str


def parse_provider(doc: dict) -> Provider:
    return Provider(
        name=doc["name"],
        typeId=doc["typeId"],
        supportedGroups=doc["supportedGroups"],
        providedVMs=doc["providedVMs"],
        storages=doc["storages"],
        providedNetworks=doc["providedNetworks"],
        description=doc["description"],
    )


@dataclass
class Storage:
    name: str
    typeId: str
    maps: str


def parse_storage(doc: dict) -> Storage:
    return Storage(
        name=doc["name"],
        typeId=doc["typeId"],
        maps=doc["maps"],
    )


@dataclass
class Network:
    name: str
    typeId: str
    maps: str


def parse_network(doc: dict) -> Network:
    return Network(
        name=doc["name"],
        typeId=doc["typeId"],
        maps=doc["maps"],
    )
