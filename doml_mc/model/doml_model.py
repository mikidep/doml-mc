from dataclasses import dataclass

from .application import Application, parse_application
from .infrastructure import Infrastructure, parse_infrastructure
from .optimization import Optimization, parse_optimization
from .concretization import Concretization, parse_concretization


@dataclass
class DOMLModel:
    name: str
    modelname: str
    id: str
    version: str
    application: Application
    infrastructure: Infrastructure
    optimization: Optimization
    concretizations: dict[str, Concretization]


def parse_doml_model(doc: dict) -> DOMLModel:
    return DOMLModel(
        name=doc["name"],
        modelname=doc["modelname"],
        id=doc["id"],
        version=doc["version"],
        application=parse_application(doc["application"]),
        infrastructure=parse_infrastructure(doc["infrastructure"]),
        optimization=parse_optimization(doc["optimization"]),
        concretizations={
            concdoc["name"]: parse_concretization(concdoc)
            for concdoc in doc["concretizations"]
        },
    )
