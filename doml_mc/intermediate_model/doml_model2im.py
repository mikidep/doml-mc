from ..model.doml_model import DOMLModel
from .doml_element import DOMLElement
from .application2im import application_to_im
from .infrastructure2im import infrastructure_to_im


def doml_model_to_im(model: DOMLModel) -> dict[str, DOMLElement]:
    return application_to_im(model.application) | infrastructure_to_im(
        model.infrastructure
    )
