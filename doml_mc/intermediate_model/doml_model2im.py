from ..model.doml_model import DOMLModel
from .types import IntermediateModel, MetaModel
from .application2im import application_to_im
from .infrastructure2im import infrastructure_to_im


def doml_model_to_im(model: DOMLModel, mm: MetaModel) -> IntermediateModel:
    return application_to_im(model.application) | infrastructure_to_im(
        model.infrastructure, mm
    )
