from ..model.application import Application, ApplicationComponent
from .doml_element import DOMLElement
from .._utils import merge_dicts


def application_to_im(app: Application) -> dict[str, DOMLElement]:
    def app_comp_to_im(
        app_comp: ApplicationComponent,
    ) -> dict[str, DOMLElement]:
        comp_elem = DOMLElement(
            name=app_comp.name,
            type=app_comp.typeId,
            attributes={},
            associations={
                "application_SoftwareComponent::consumedInterfaces": {
                    f"{cn}_{ifacen}"
                    for cn, ifacens in app_comp.consumedInterfaces.items()
                    for ifacen in ifacens
                },
                "application_SoftwareComponent::exposedInterfaces": {
                    f"{app_comp.name}_{ifacen}"
                    for ifacen in app_comp.exposedInterfaces
                },
            },
        )

        iface_elems = {
            f"{app_comp.name}_{ifacen}": DOMLElement(
                name=f"{app_comp.name}_{ifacen}",
                type="application_SoftwareInterface",
                attributes={
                    "application_SoftwareInterface::endPoint": iface.endPoint
                },
                associations={},
            )
            for ifacen, iface in app_comp.exposedInterfaces.items()
        }

        return {app_comp.name: comp_elem} | iface_elems

    return merge_dicts(app_comp_to_im(comp) for comp in app.children.values())
