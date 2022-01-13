from dataclasses import dataclass


@dataclass
class Application:
    name: str
    children: dict[str, "ApplicationComponent"]


def parse_application(doc: dict) -> Application:
    return Application(
        name=doc["name"],
        children={
            compdoc["name"]: parse_application_component(compdoc)
            for compdoc in doc["children"]
        },
    )


@dataclass
class ApplicationComponent:
    typeId: str
    name: str
    consumedInterfaces: dict[str, list[str]]
    exposedInterfaces: dict[str, "ApplicationInterface"]


def parse_application_component(doc: dict) -> ApplicationComponent:
    def remove_prefix(s: str, prefix: str) -> str:
        if s.startswith(prefix):
            return s[len(prefix) :]
        else:
            return s

    return ApplicationComponent(
        name=doc["name"],
        typeId=doc["typeId"],
        consumedInterfaces={
            remove_prefix(k, "consumedInterfaces->"): d
            for k, d in doc.items()
            if k.startswith("consumedInterfaces->")
        },
        exposedInterfaces={
            intdoc["name"]: parse_application_interface(intdoc, doc["name"])
            for intdoc in doc.get("exposedInterfaces", [])
        },
    )


@dataclass
class ApplicationInterface:
    name: str
    componentName: str
    typeId: str
    endPoint: str


def parse_application_interface(
    doc: dict, componentName: str
) -> ApplicationInterface:
    return ApplicationInterface(
        name=doc["name"],
        componentName=componentName,
        typeId=doc["typeId"],
        endPoint=doc["endPoint"],
    )
