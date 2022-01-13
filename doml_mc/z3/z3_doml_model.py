from z3 import Solver

from ..model.doml_model import DOMLModel
from .application import (
    def_and_assert_app_type_function,
    def_and_assert_consumes_relation,
    mk_application_component_sort,
    mk_application_interface_sort,
    mk_application_type_sort,
)
from .infrastructure import (
    def_and_assert_infra_group_type_function,
    def_and_assert_infra_node_type_function,
    def_and_assert_network_first_address_function,
    def_and_assert_network_last_address_function,
    def_and_assert_network_protocol_function,
    mk_infrastructure_group_sort,
    mk_infrastructure_group_type_sort,
    mk_infrastructure_network_sort,
    mk_infrastructure_node_sort,
    mk_infrastructure_node_type_sort,
    mk_network_protocol_sort,
)


class Z3DOMLModel:
    def __init__(self, doml_model: DOMLModel) -> None:
        self.solver = Solver()

        #########################
        #   Application Layer   #
        #########################

        self.app_comp_sort, self.app_comp = mk_application_component_sort(
            doml_model.application
        )
        self.app_type_sort, self.app_type_f = mk_application_type_sort(
            doml_model.application
        )
        self.app_type_f = def_and_assert_app_type_function(
            doml_model.application,
            self.solver,
            self.app_comp_sort,
            self.app_comp,
            self.app_type_sort,
            self.app_type_f,
        )
        self.app_iface_sort, self.app_iface = mk_application_interface_sort(
            doml_model.application
        )
        self.consumes_rel = def_and_assert_consumes_relation(
            doml_model.application,
            self.solver,
            self.app_comp_sort,
            self.app_comp,
            self.app_iface_sort,
            self.app_iface,
        )

        ############################
        #   Infrastructure Layer   #
        ############################

        self.infra_node_sort, self.infra_node = mk_infrastructure_node_sort(
            doml_model.infrastructure
        )
        (
            self.infra_node_type_sort,
            self.infra_node_type,
        ) = mk_infrastructure_node_type_sort(doml_model.infrastructure)
        self.infra_node_type_f = def_and_assert_infra_node_type_function(
            doml_model.infrastructure,
            self.solver,
            self.infra_node_sort,
            self.infra_node,
            self.infra_node_type_sort,
            self.infra_node_type,
        )
        (
            self.infra_network_sort,
            self.infra_network,
        ) = mk_infrastructure_network_sort(doml_model.infrastructure)
        (
            self.network_proto_sort,
            self.network_proto,
        ) = mk_network_protocol_sort()
        self.nework_proto_f = def_and_assert_network_protocol_function(
            doml_model.infrastructure,
            self.solver,
            self.infra_network_sort,
            self.infra_network,
            self.network_proto_sort,
            self.network_proto,
        )
        self.network_first_addr_f = (
            def_and_assert_network_first_address_function(
                doml_model.infrastructure,
                self.solver,
                self.infra_network_sort,
                self.infra_network,
            )
        )
        self.network_last_addr_f = (
            def_and_assert_network_last_address_function(
                doml_model.infrastructure,
                self.solver,
                self.infra_network_sort,
                self.infra_network,
            )
        )
        self.infra_group_sort, self.infra_group = mk_infrastructure_group_sort(
            doml_model.infrastructure
        )
        (
            self.infra_group_type_sort,
            self.infra_group_type,
        ) = mk_infrastructure_group_type_sort(doml_model.infrastructure)
        self.infra_group_type_f = def_and_assert_infra_group_type_function(
            doml_model.infrastructure,
            self.solver,
            self.infra_group_sort,
            self.infra_group,
            self.infra_group_type_sort,
            self.infra_group_type,
        )
