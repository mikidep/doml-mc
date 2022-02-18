from time import perf_counter

last_time: float = 0.0


class bcolors:
    HEADER = "\033[95m"
    OKBLUE = "\033[94m"
    OKCYAN = "\033[96m"
    OKGREEN = "\033[92m"
    WARNING = "\033[93m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"
    BOLD = "\033[1m"
    UNDERLINE = "\033[4m"


def tic():
    global last_time
    last_time = perf_counter()


def toc_tic(label: str):
    global last_time
    toc = perf_counter()
    print(
        f"{bcolors.BOLD}{bcolors.OKGREEN}TOC! "
        + f"{label}:{bcolors.ENDC} {toc - last_time} s."
    )
    last_time = toc


tic()

from ipaddress import ip_address, ip_network

from z3 import (
    And,
    BoolSort,
    Const,
    Consts,
    Datatype,
    Exists,
    ForAll,
    Function,
    Implies,
    IntSort,
    Or,
    sat,
    set_param,
    Solver,
)

set_param("smt.macro_finder", True)


from doml_mc.z3.utils import (
    assert_function_tuples,
    assert_relation_tuples,
    Iff,
    mk_enum_sort_dict,
    mk_stringsym_sort_dict,
)

toc_tic("Imports")

solver = Solver()

toc_tic("Solver init")

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

toc_tic("Elements and classes")

##################
#   ATTRIBUTES   #
##################

ss_sort, ss = mk_stringsym_sort_dict(
    [
        "099720109477",
        "13.1",
        "SCSI",
        "concrete_net",
        "danilo",
        "db.t3.micro",
        "debian-cloud/debian-9",
        "default",
        "education",
        "hosted_on wp_vm1",
        "passw0rd",
        "piacere_subnet",
        "piacere_vpc",
        "postgres",
        "t2.large",
        "t2.micro",
        "tcp/ip",
        "ubuntu*",
        "ubuntu_ami",
        "us-central1",
        "vpc_network",
        "wp_db",
    ]
)

AData = Datatype("AttributeData")
AData.declare("int", ("get_int", IntSort()))
AData.declare("bool", ("get_bool", BoolSort()))
AData.declare("ss", ("get_ss", ss_sort))
AData = AData.create()

attr_sort, attr = mk_enum_sort_dict(
    "Attribute",
    [
        "DBMS::identifier",
        "DBMS::engine",
        "DBMS::engine_version",
        "DBMS::username",
        "DBMS::password",
        "DBMS::name",
        "NetworkInterface::address",
        "Network::address_lb",
        "Network::address_ub",
        "Network::protocol",
    ],
)

attr_rel = Function("attribute", elem_sort, attr_sort, AData, BoolSort())

a = Const("a", attr_sort)
d = Const("d", AData)
solver.append(
    ForAll(
        [a, d],
        And(
            Iff(
                attr_rel(elem["database"], a, d),
                Or(
                    And(
                        a == attr["DBMS::identifier"],
                        d == AData.ss(ss["education"]),
                    ),
                    And(
                        a == attr["DBMS::engine"],
                        d == AData.ss(ss["postgres"]),
                    ),
                    And(
                        a == attr["DBMS::engine_version"],
                        d == AData.ss(ss["13.1"]),
                    ),
                    And(
                        a == attr["DBMS::username"],
                        d == AData.ss(ss["danilo"]),
                    ),
                    And(
                        a == attr["DBMS::password"],
                        d == AData.ss(ss["passw0rd"]),
                    ),
                    And(
                        a == attr["DBMS::name"],
                        d == AData.ss(ss["wp_db"]),
                    ),
                ),
            ),
            Iff(
                attr_rel(elem["i1"], a, d),
                And(
                    a == attr["NetworkInterface::address"],
                    d == AData.int(int(ip_address("10.0.1.3"))),
                ),
            ),
            Iff(
                attr_rel(elem["i2"], a, d),
                And(
                    a == attr["NetworkInterface::address"],
                    d == AData.int(int(ip_address("10.0.1.1"))),
                ),
            ),
            Iff(
                attr_rel(elem["i3"], a, d),
                And(
                    a == attr["NetworkInterface::address"],
                    d == AData.int(int(ip_address("10.0.1.2"))),
                ),
            ),
            Iff(
                attr_rel(elem["net1"], a, d),
                Or(
                    And(
                        a == attr["Network::address_lb"],
                        d == AData.int(int(ip_network("10.0.1.0/24")[0])),
                    ),
                    And(
                        a == attr["Network::address_ub"],
                        d == AData.int(int(ip_network("10.0.1.0/24")[-1])),
                    ),
                    And(
                        a == attr["Network::protocol"],
                        d == AData.ss(ss["tcp/ip"]),
                    ),
                ),
            ),
        ),
    )
)

toc_tic("Attributes")

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

toc_tic("Associations")

##########################
#   EXAMPLE PROPERTIES   #
##########################

# All software packages can see the interfaces they need through a common
# network.
spp, spc, i, n, ni, cn, c, d, dc = Consts(
    "spp spc i n ni cn c d dc", elem_sort
)
attr = ForAll(
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
solver.assert_and_track(attr, "software_package_iface_net")

toc_tic("Example properties")

###############
#   SOLVING   #
###############

# print(solver.sexpr())

is_sat = solver.check()
print(is_sat)
if is_sat == sat:
    solver.model()
else:
    print(solver.unsat_core())

toc_tic("Solving")
with open("sexpr.smt", "w") as sexprf:
    sexprf.write(solver.sexpr())
