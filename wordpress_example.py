import itertools

from z3 import (
    EnumSort,
    Function,
    DatatypeSortRef,
    DatatypeRef,
    FuncDeclRef,
    Solver,
    Const,
    Not,
    Implies,
    IntSort,
    BoolSort,
    sat,
)


def mk_enum_sort_dict(
    name: str, values: list[str]
) -> tuple[DatatypeSortRef, dict[str, DatatypeRef]]:
    sort, dtrefs = EnumSort(name, values)
    return sort, dict(zip(values, dtrefs))


def ip_to_int(a: int, b: int, c: int, d: int) -> int:
    return (a << 24) + (b << 16) + (c << 8) + d


def assert_function_values(
    f: FuncDeclRef, s: Solver, tpls: list[tuple]
) -> None:
    for tpl in tpls:
        xs = tpl[:-1]
        y = tpl[-1]
        s.assert_and_track(f(*xs) == y, f"{f}@{' '.join(str(x) for x in tpl)}")


solver = Solver()
solver.set(unsat_core=True)

enty_sort, enty = mk_enum_sort_dict(
    "Entity",
    [
        # Application layer
        "database",
        "wordPressServer",
        # Infrastructure layer
        "container1",
        "container2",
        "container1_image",
        "wp_vm1",
        "wp_vm2",
        "dbms_vm",
        "net1",
        "g1",
    ],
)

kind_sort, kind = mk_enum_sort_dict(
    "Kind",
    [
        # Application
        "dbms",
        "software_component",
        # Infrastructure
        "container",
        "cont_image",
        "vm",
        "net",
        "autoscale_group",
    ],
)

kind_f = Function("kind", enty_sort, kind_sort)
assert_function_values(
    kind_f,
    solver,
    [
        # Application
        (enty["database"], kind["dbms"]),
        (enty["wordPressServer"], kind["software_component"]),
        # Infrastructure
        (enty["container1"], kind["container"]),
        (enty["container2"], kind["container"]),
        (enty["container1_image"], kind["cont_image"]),
        (enty["wp_vm1"], kind["vm"]),
        (enty["wp_vm2"], kind["vm"]),
        (enty["dbms_vm"], kind["vm"]),
        (enty["net1"], kind["net"]),
        (enty["g1"], kind["autoscale_group"]),
    ],
)

layer_sort, layer = mk_enum_sort_dict(
    "Layer",
    [
        "application",
        "infrastructure",
        "concretization",
    ],
)

kind_layer_f = Function("kind_layer", kind_sort, layer_sort)
assert_function_values(
    kind_layer_f,
    solver,
    [
        # Application
        (kind["dbms"], layer["application"]),
        (kind["software_component"], layer["application"]),
        # Infrastructure
        (kind["container"], layer["infrastructure"]),
        (kind["cont_image"], layer["infrastructure"]),
        (kind["vm"], layer["infrastructure"]),
        (kind["net"], layer["infrastructure"]),
        (kind["autoscale_group"], layer["infrastructure"]),
    ],
)

cap_sort, cap = mk_enum_sort_dict(
    "Capability",
    [
        "SQL_interface",
    ],
)

provides_consumes_rel = Function(
    "provides_consumes", enty_sort, cap_sort, enty_sort, BoolSort()
)
provides_consumes_tuples = {
    ("database", "SQL_interface", "wordPressServer"),
}

for e1n, capn, e2n in itertools.product(enty, cap, enty):
    if (e1n, capn, e2n) in provides_consumes_tuples:
        solver.add(provides_consumes_rel(enty[e1n], cap[capn], enty[e2n]))
    else:
        solver.add(Not(provides_consumes_rel(enty[e1n], cap[capn], enty[e2n])))

##################
#   DEPLOYMENT   #
##################

deployment_sort, deployment = mk_enum_sort_dict("Deployment", ["config1"])

deploy_rel = Function(
    "deploy", enty_sort, deployment_sort, enty_sort, BoolSort()
)
deploy_tuples = {
    ("container1", "config1", "wp_vm1"),
    ("container2", "config1", "wp_vm2"),
    ("wordPressServer", "config1", "container1"),
    ("wordPressServer", "config1", "container2"),
    ("database", "config1", "dbms_vm"),
}

for e1n, dep, e2n in itertools.product(enty, deployment, enty):
    if (e1n, dep, e2n) in deploy_tuples:
        solver.add(deploy_rel(enty[e1n], deployment[dep], enty[e2n]))
    else:
        solver.add(Not(deploy_rel(enty[e1n], deployment[dep], enty[e2n])))

# forall x, (exists y, deploy(y, _, x)) -> layer(kind(x)) = infrastructure
for (_, _, x) in deploy_tuples:
    solver.assert_and_track(
        kind_layer_f(kind_f(enty[x])) == layer["infrastructure"],
        "deploy_infra@" + x,
    )

active_dep = Const("active_deployment", deployment_sort)
solver.add(active_dep == deployment["config1"])

###############
#   NETWORK   #
###############

iface_sort, iface = mk_enum_sort_dict(
    "Iface",
    [
        "wp_vm1::i1",
        "wp_vm2::i1",
        "dbms_vm::i1",
    ],
)

iface_enty_f = Function("iface_enty", iface_sort, enty_sort)
assert_function_values(
    iface_enty_f,
    solver,
    [
        (iface["wp_vm1::i1"], enty["wp_vm1"]),
        (iface["wp_vm2::i1"], enty["wp_vm2"]),
        (iface["dbms_vm::i1"], enty["dbms_vm"]),
    ],
)

iface_ip_f = Function("iface_ip", iface_sort, IntSort())
assert_function_values(
    iface_ip_f,
    solver,
    [
        (iface["wp_vm1::i1"], ip_to_int(10, 0, 1, 3)),
        (iface["wp_vm2::i1"], ip_to_int(10, 0, 1, 1)),
        (iface["dbms_vm::i1"], ip_to_int(10, 0, 1, 2)),
    ],
)

# distinct ifaces have distinct IPs
for i1n, i2n in itertools.product(iface, iface):
    solver.assert_and_track(
        Implies(
            iface_ip_f(iface[i1n]) == iface_ip_f(iface[i2n]),
            iface[i1n] == iface[i2n],
        ),
        f"distinct_ips@{i1n} {i2n}",
    )

#######################
#   CONCRETIZATIONS   #
#######################

provider_sort, provider = mk_enum_sort_dict(
    "Provider", ["aws", "azure", "docker", "gcp"]
)

con_infra_sort, con_infra = mk_enum_sort_dict(
    "ConcreteInfrastructure", ["con_infra1", "con_infra2"]
)


###############
#   SOLVING   #
###############

print(solver.sexpr())

is_sat = solver.check()
print(is_sat)
if is_sat == sat:
    print(solver.model())
else:
    print(solver.unsat_core())
