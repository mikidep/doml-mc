from z3 import (
    And,
    BoolSort,
    Consts,
    Exists,
    ForAll,
    Function,
    Implies,
    Or,
    sat,
    Solver,
)

from doml_mc.z3.utils import (
    assert_relation_tuples,
    mk_enum_sort_dict,
    assert_function_tuples,
)

solver = Solver()

############################
#   ELEMENTS AND CLASSES   #
############################

elem_sort, elem = mk_enum_sort_dict(
    "Element",
    [
        # structural elements
        "app",
        "infra",
        "config1",
        "dpl1",
        "dpl2",
        "dpl3",
        "dpl4",
        "dpl5",
        # application layer
        "database",
        "wordPressServer",
        "SQL_interface",
        # infrastructure layer
        "container1",
        "container2",
        "container1_image",
        "wp_vm1",
        "wp_vm2",
        "dbms_vm",
        "net1",
        "i1",
        "i2",
        "i3",
        "g1",
    ],
)

class_sort, class_ = mk_enum_sort_dict(
    "Class",
    [
        "ApplicationLayer",
        "InfrastructureLayer",
        "Configuration",
        "Deployment",
        "DBMS",
        "SoftwarePackage",
        "SoftwareInterface",
        "Container",
        "ContainerImage",
        "VirtualMachine",
        "Network",
        "NetworkInterface",
        "AutoScalingGroup",
    ],
)

elem_class_f = Function("elem_class", elem_sort, class_sort)
assert_function_tuples(
    elem_class_f,
    solver,
    [
        # structural elements
        ["app", "ApplicationLayer"],
        ["infra", "InfrastructureLayer"],
        ["config1", "Configuration"],
        ["dpl1", "Deployment"],
        ["dpl2", "Deployment"],
        ["dpl3", "Deployment"],
        ["dpl4", "Deployment"],
        ["dpl5", "Deployment"],
        # application layer
        ["database", "DBMS"],
        ["wordPressServer", "SoftwarePackage"],
        ["SQL_interface", "SoftwareInterface"],
        # infrastructure layer
        ["container1", "Container"],
        ["container2", "Container"],
        ["container1_image", "ContainerImage"],
        ["wp_vm1", "VirtualMachine"],
        ["wp_vm2", "VirtualMachine"],
        ["dbms_vm", "VirtualMachine"],
        ["net1", "Network"],
        ["i1", "NetworkInterface"],
        ["i2", "NetworkInterface"],
        ["i3", "NetworkInterface"],
        ["g1", "AutoScalingGroup"],
    ],
    elem,
    class_,
)

####################
#   ASSOCIATIONS   #
####################

assoc_sort, assoc = mk_enum_sort_dict(
    "Association",
    [
        "SoftwarePackage::exposedInterfaces",
        "SoftwarePackage::consumedInterfaces",
        "ContainerImage::generatedContainers",
        "ComputingNode::ifaces",
        "NetworkInterface::belongsTo",
        "AutoScalingGroup::groupedNodes",
        "Configuration::deployments",
        "Deployment::source",
        "Deployment::target",
    ],
)

assoc_rel = Function(
    "association", elem_sort, assoc_sort, elem_sort, BoolSort()
)
assert_relation_tuples(
    assoc_rel,
    solver,
    [
        ["database", "SoftwarePackage::exposedInterfaces", "SQL_interface"],
        [
            "wordPressServer",
            "SoftwarePackage::consumedInterfaces",
            "SQL_interface",
        ],
        [
            "container1_image",
            "ContainerImage::generatedContainers",
            "container1",
        ],
        [
            "container1_image",
            "ContainerImage::generatedContainers",
            "container2",
        ],
        ["wp_vm1", "ComputingNode::ifaces", "i1"],
        ["wp_vm2", "ComputingNode::ifaces", "i2"],
        ["dbms_vm", "ComputingNode::ifaces", "i3"],
        ["i1", "NetworkInterface::belongsTo", "net1"],
        ["i2", "NetworkInterface::belongsTo", "net1"],
        ["i3", "NetworkInterface::belongsTo", "net1"],
        ["g1", "AutoScalingGroup::groupedNodes", "wp_vm1"],
        ["g1", "AutoScalingGroup::groupedNodes", "wp_vm2"],
        ["config1", "Configuration::deployments", "dpl1"],
        ["config1", "Configuration::deployments", "dpl2"],
        ["config1", "Configuration::deployments", "dpl3"],
        ["config1", "Configuration::deployments", "dpl4"],
        ["config1", "Configuration::deployments", "dpl5"],
        ["dpl1", "Deployment::source", "container1"],
        ["dpl1", "Deployment::target", "wp_vm1"],
        ["dpl2", "Deployment::source", "container2"],
        ["dpl2", "Deployment::target", "wp_vm2"],
        ["dpl3", "Deployment::source", "wordPressServer"],
        ["dpl3", "Deployment::target", "container1"],
        ["dpl4", "Deployment::source", "wordPressServer"],
        ["dpl4", "Deployment::target", "container2"],
        # Try commenting out these two tuples
        ["dpl5", "Deployment::source", "database"],
        ["dpl5", "Deployment::target", "dbms_vm"],
    ],
    elem,
    assoc,
    elem,
)

##########################
#   EXAMPLE PROPERTIES   #
##########################

# All software packages can see the interfaces they need through a common
# network.
spp, spc, i, n, ni, cn, c, d, dc = Consts(
    "spp spc i n ni cn c d dc", elem_sort
)
prop = ForAll(
    [spp, spc, i],
    Implies(
        And(
            assoc_rel(spp, assoc["SoftwarePackage::exposedInterfaces"], i),
            assoc_rel(spc, assoc["SoftwarePackage::consumedInterfaces"], i),
        ),
        Exists(
            [n],
            And(
                Or(
                    Exists(
                        [cn, d, ni],
                        And(
                            assoc_rel(d, assoc["Deployment::source"], spp),
                            assoc_rel(d, assoc["Deployment::target"], cn),
                            assoc_rel(cn, assoc["ComputingNode::ifaces"], ni),
                            assoc_rel(
                                ni, assoc["NetworkInterface::belongsTo"], n
                            ),
                        ),
                    ),
                    Exists(
                        [cn, d, c, dc, ni],
                        And(
                            assoc_rel(d, assoc["Deployment::source"], spp),
                            assoc_rel(d, assoc["Deployment::target"], c),
                            assoc_rel(dc, assoc["Deployment::source"], c),
                            assoc_rel(dc, assoc["Deployment::target"], cn),
                            assoc_rel(cn, assoc["ComputingNode::ifaces"], ni),
                            assoc_rel(
                                ni, assoc["NetworkInterface::belongsTo"], n
                            ),
                        ),
                    ),
                ),
                Or(
                    Exists(
                        [cn, d, ni],
                        And(
                            assoc_rel(d, assoc["Deployment::source"], spc),
                            assoc_rel(d, assoc["Deployment::target"], cn),
                            assoc_rel(cn, assoc["ComputingNode::ifaces"], ni),
                            assoc_rel(
                                ni, assoc["NetworkInterface::belongsTo"], n
                            ),
                        ),
                    ),
                    Exists(
                        [cn, d, c, dc, ni],
                        And(
                            assoc_rel(d, assoc["Deployment::source"], spc),
                            assoc_rel(d, assoc["Deployment::target"], c),
                            assoc_rel(dc, assoc["Deployment::source"], c),
                            assoc_rel(dc, assoc["Deployment::target"], cn),
                            assoc_rel(cn, assoc["ComputingNode::ifaces"], ni),
                            assoc_rel(
                                ni, assoc["NetworkInterface::belongsTo"], n
                            ),
                        ),
                    ),
                ),
            ),
        ),
    ),
)
solver.assert_and_track(prop, "software_package_iface_net")


###############
#   SOLVING   #
###############

# print(solver.sexpr())

is_sat = solver.check()
print(is_sat)
if is_sat == sat:
    print(solver.model())
else:
    print(solver.unsat_core())
