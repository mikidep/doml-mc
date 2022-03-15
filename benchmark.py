from dataclasses import dataclass
import json
import yaml
from z3 import Consts, ForAll, Exists, Implies, And, Or, Solver, unsat


from doml_mc.model.doml_model import parse_doml_model
from doml_mc.intermediate_model.doml_model2im import doml_model_to_im
from doml_mc.intermediate_model.doml_element import (
    reciprocate_inverse_associations,
)
from doml_mc.intermediate_model.metamodel import (
    parse_metamodel,
    parse_inverse_associations,
)
from doml_mc.z3.metamodel_encoding import (
    def_association_rel_and_assert_constraints,
    def_attribute_rel_and_assert_constraints,
    mk_association_sort_dict,
    mk_attribute_sort_dict,
    mk_class_sort_dict,
)
from doml_mc.z3.im_encoding import (
    assert_im_associations_q,
    assert_im_attributes,
    def_elem_class_f_and_assert_classes,
    mk_elem_sort_dict,
    mk_stringsym_sort_dict,
)
from doml_mc.z3.utils import mk_adata_sort


with open("assets/doml_meta.yaml") as mmf:
    mmdoc = yaml.load(mmf, yaml.Loader)
mm = parse_metamodel(mmdoc)
inv_assoc = parse_inverse_associations(mmdoc)


@dataclass
class BenchmarkRes:
    time: float
    q_inst: int
    conflicts: int
    memory: float


@dataclass
class Benchmark:
    doml_document_path: str
    unbound_elems_n: int

    def perform_first_solving(self) -> BenchmarkRes:
        with open(self.doml_document_path) as jsonf:
            doc = json.load(jsonf)

        doml_model = parse_doml_model(doc, mm)

        im = doml_model_to_im(doml_model, mm)
        reciprocate_inverse_associations(im, inv_assoc)

        unbound_elems = [f"unbound{i}" for i in range(self.unbound_elems_n)]

        solver = Solver()

        class_sort, class_ = mk_class_sort_dict(mm)
        assoc_sort, assoc = mk_association_sort_dict(mm)
        attr_sort, attr = mk_attribute_sort_dict(mm)
        elem_sort, elem = mk_elem_sort_dict(im, unbound_elems)
        ss_sort, ss = mk_stringsym_sort_dict(im, mm)
        AData = mk_adata_sort(ss_sort)
        elem_class_f = def_elem_class_f_and_assert_classes(
            im, solver, elem_sort, elem, class_sort, class_
        )
        attr_rel = def_attribute_rel_and_assert_constraints(
            mm,
            solver,
            attr_sort,
            attr,
            class_,
            elem_class_f,
            elem_sort,
            AData,
            ss,
        )
        assert_im_attributes(
            attr_rel, solver, im, mm, elem, attr_sort, attr, AData, ss
        )
        assoc_rel = def_association_rel_and_assert_constraints(
            mm,
            solver,
            assoc_sort,
            assoc,
            class_,
            elem_class_f,
            elem_sort,
            inv_assoc,
        )
        assert_im_associations_q(
            assoc_rel,
            solver,
            {k: v for k, v in im.items() if k not in unbound_elems},
            elem,
            assoc_sort,
            assoc,
        )

        is_sat = solver.check()
        if is_sat == unsat:
            print("UNSAT!")

        stats = solver.statistics()
        return BenchmarkRes(
            time=stats.time,
            q_inst=stats.quant_instantiations,
            conflicts=stats.conflicts,
            memory=stats.memory,
        )

    def perform_incr_solving(self) -> BenchmarkRes:
        with open(self.doml_document_path) as jsonf:
            doc = json.load(jsonf)

        doml_model = parse_doml_model(doc, mm)

        im = doml_model_to_im(doml_model, mm)
        reciprocate_inverse_associations(im, inv_assoc)

        unbound_elems = [f"unbound{i}" for i in range(self.unbound_elems_n)]

        solver = Solver()

        class_sort, class_ = mk_class_sort_dict(mm)
        assoc_sort, assoc = mk_association_sort_dict(mm)
        attr_sort, attr = mk_attribute_sort_dict(mm)
        elem_sort, elem = mk_elem_sort_dict(im, unbound_elems)
        ss_sort, ss = mk_stringsym_sort_dict(im, mm)
        AData = mk_adata_sort(ss_sort)
        elem_class_f = def_elem_class_f_and_assert_classes(
            im, solver, elem_sort, elem, class_sort, class_
        )
        attr_rel = def_attribute_rel_and_assert_constraints(
            mm,
            solver,
            attr_sort,
            attr,
            class_,
            elem_class_f,
            elem_sort,
            AData,
            ss,
        )
        assert_im_attributes(
            attr_rel, solver, im, mm, elem, attr_sort, attr, AData, ss
        )
        assoc_rel = def_association_rel_and_assert_constraints(
            mm,
            solver,
            assoc_sort,
            assoc,
            class_,
            elem_class_f,
            elem_sort,
            inv_assoc,
        )
        assert_im_associations_q(
            assoc_rel,
            solver,
            {k: v for k, v in im.items() if k not in unbound_elems},
            elem,
            assoc_sort,
            assoc,
        )

        is_sat = solver.check()
        if is_sat == unsat:
            print("UNSAT!")

        spp, spc, i, n, ni, cn, c, d, dc = Consts(
            "spp spc i n ni cn c d dc", elem_sort
        )
        assn = ForAll(
            [spp, spc, i],
            Implies(
                And(
                    assoc_rel(
                        spp,
                        assoc[
                            "application_SoftwarePackage::exposedInterfaces"
                        ],
                        i,
                    ),
                    assoc_rel(
                        spc,
                        assoc[
                            "application_SoftwarePackage::consumedInterfaces"
                        ],
                        i,
                    ),
                ),
                Exists(
                    [n],
                    And(
                        Or(
                            Exists(
                                [cn, d, ni],
                                And(
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::source"],
                                        spp,
                                    ),
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::target"],
                                        cn,
                                    ),
                                    assoc_rel(
                                        cn,
                                        assoc[
                                            "infrastructure_ComputingNode::ifaces"
                                        ],
                                        ni,
                                    ),
                                    assoc_rel(
                                        ni,
                                        assoc[
                                            "infrastructure_NetworkInterface::belongsTo"
                                        ],
                                        n,
                                    ),
                                ),
                            ),
                            Exists(
                                [cn, d, c, dc, ni],
                                And(
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::source"],
                                        spp,
                                    ),
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::target"],
                                        c,
                                    ),
                                    assoc_rel(
                                        dc,
                                        assoc["commons_Deployment::source"],
                                        c,
                                    ),
                                    assoc_rel(
                                        dc,
                                        assoc["commons_Deployment::target"],
                                        cn,
                                    ),
                                    assoc_rel(
                                        cn,
                                        assoc[
                                            "infrastructure_ComputingNode::ifaces"
                                        ],
                                        ni,
                                    ),
                                    assoc_rel(
                                        ni,
                                        assoc[
                                            "infrastructure_NetworkInterface::belongsTo"
                                        ],
                                        n,
                                    ),
                                ),
                            ),
                        ),
                        Or(
                            Exists(
                                [cn, d, ni],
                                And(
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::source"],
                                        spc,
                                    ),
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::target"],
                                        cn,
                                    ),
                                    assoc_rel(
                                        cn,
                                        assoc[
                                            "infrastructure_ComputingNode::ifaces"
                                        ],
                                        ni,
                                    ),
                                    assoc_rel(
                                        ni,
                                        assoc[
                                            "infrastructure_NetworkInterface::belongsTo"
                                        ],
                                        n,
                                    ),
                                ),
                            ),
                            Exists(
                                [cn, d, c, dc, ni],
                                And(
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::source"],
                                        spc,
                                    ),
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::target"],
                                        c,
                                    ),
                                    assoc_rel(
                                        dc,
                                        assoc["commons_Deployment::source"],
                                        c,
                                    ),
                                    assoc_rel(
                                        dc,
                                        assoc["commons_Deployment::target"],
                                        cn,
                                    ),
                                    assoc_rel(
                                        cn,
                                        assoc[
                                            "infrastructure_ComputingNode::ifaces"
                                        ],
                                        ni,
                                    ),
                                    assoc_rel(
                                        ni,
                                        assoc[
                                            "infrastructure_NetworkInterface::belongsTo"
                                        ],
                                        n,
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )
        solver.assert_and_track(assn, "software_package_iface_net")

        e1, e2, ni = Consts("e1 e2 i", elem_sort)
        assn = ForAll(
            [e1, e2, ni],
            Implies(
                And(
                    Or(
                        assoc_rel(
                            e1,
                            assoc["infrastructure_ComputingNode::ifaces"],
                            ni,
                        ),
                        assoc_rel(
                            e1, assoc["infrastructure_Storage::ifaces"], ni
                        ),
                    ),
                    Or(
                        assoc_rel(
                            e2,
                            assoc["infrastructure_ComputingNode::ifaces"],
                            ni,
                        ),
                        assoc_rel(
                            e2, assoc["infrastructure_Storage::ifaces"], ni
                        ),
                    ),
                ),
                e1 == e2,
            ),
        )
        solver.assert_and_track(assn, "iface_uniq")

        is_sat = solver.check()
        if is_sat == unsat:
            print("UNSAT!")
        stats = solver.statistics()
        return BenchmarkRes(
            time=stats.time,
            q_inst=stats.quant_instantiations,
            conflicts=stats.conflicts,
            memory=stats.memory,
        )

    def perform_cmlt_solving(self) -> BenchmarkRes:
        with open(self.doml_document_path) as jsonf:
            doc = json.load(jsonf)

        doml_model = parse_doml_model(doc, mm)

        im = doml_model_to_im(doml_model, mm)
        reciprocate_inverse_associations(im, inv_assoc)

        unbound_elems = [f"unbound{i}" for i in range(self.unbound_elems_n)]

        solver = Solver()

        class_sort, class_ = mk_class_sort_dict(mm)
        assoc_sort, assoc = mk_association_sort_dict(mm)
        attr_sort, attr = mk_attribute_sort_dict(mm)
        elem_sort, elem = mk_elem_sort_dict(im, unbound_elems)
        ss_sort, ss = mk_stringsym_sort_dict(im, mm)
        AData = mk_adata_sort(ss_sort)
        elem_class_f = def_elem_class_f_and_assert_classes(
            im, solver, elem_sort, elem, class_sort, class_
        )
        attr_rel = def_attribute_rel_and_assert_constraints(
            mm,
            solver,
            attr_sort,
            attr,
            class_,
            elem_class_f,
            elem_sort,
            AData,
            ss,
        )
        assert_im_attributes(
            attr_rel, solver, im, mm, elem, attr_sort, attr, AData, ss
        )
        assoc_rel = def_association_rel_and_assert_constraints(
            mm,
            solver,
            assoc_sort,
            assoc,
            class_,
            elem_class_f,
            elem_sort,
            inv_assoc,
        )
        assert_im_associations_q(
            assoc_rel,
            solver,
            {k: v for k, v in im.items() if k not in unbound_elems},
            elem,
            assoc_sort,
            assoc,
        )

        spp, spc, i, n, ni, cn, c, d, dc = Consts(
            "spp spc i n ni cn c d dc", elem_sort
        )
        assn = ForAll(
            [spp, spc, i],
            Implies(
                And(
                    assoc_rel(
                        spp,
                        assoc[
                            "application_SoftwarePackage::exposedInterfaces"
                        ],
                        i,
                    ),
                    assoc_rel(
                        spc,
                        assoc[
                            "application_SoftwarePackage::consumedInterfaces"
                        ],
                        i,
                    ),
                ),
                Exists(
                    [n],
                    And(
                        Or(
                            Exists(
                                [cn, d, ni],
                                And(
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::source"],
                                        spp,
                                    ),
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::target"],
                                        cn,
                                    ),
                                    assoc_rel(
                                        cn,
                                        assoc[
                                            "infrastructure_ComputingNode::ifaces"
                                        ],
                                        ni,
                                    ),
                                    assoc_rel(
                                        ni,
                                        assoc[
                                            "infrastructure_NetworkInterface::belongsTo"
                                        ],
                                        n,
                                    ),
                                ),
                            ),
                            Exists(
                                [cn, d, c, dc, ni],
                                And(
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::source"],
                                        spp,
                                    ),
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::target"],
                                        c,
                                    ),
                                    assoc_rel(
                                        dc,
                                        assoc["commons_Deployment::source"],
                                        c,
                                    ),
                                    assoc_rel(
                                        dc,
                                        assoc["commons_Deployment::target"],
                                        cn,
                                    ),
                                    assoc_rel(
                                        cn,
                                        assoc[
                                            "infrastructure_ComputingNode::ifaces"
                                        ],
                                        ni,
                                    ),
                                    assoc_rel(
                                        ni,
                                        assoc[
                                            "infrastructure_NetworkInterface::belongsTo"
                                        ],
                                        n,
                                    ),
                                ),
                            ),
                        ),
                        Or(
                            Exists(
                                [cn, d, ni],
                                And(
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::source"],
                                        spc,
                                    ),
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::target"],
                                        cn,
                                    ),
                                    assoc_rel(
                                        cn,
                                        assoc[
                                            "infrastructure_ComputingNode::ifaces"
                                        ],
                                        ni,
                                    ),
                                    assoc_rel(
                                        ni,
                                        assoc[
                                            "infrastructure_NetworkInterface::belongsTo"
                                        ],
                                        n,
                                    ),
                                ),
                            ),
                            Exists(
                                [cn, d, c, dc, ni],
                                And(
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::source"],
                                        spc,
                                    ),
                                    assoc_rel(
                                        d,
                                        assoc["commons_Deployment::target"],
                                        c,
                                    ),
                                    assoc_rel(
                                        dc,
                                        assoc["commons_Deployment::source"],
                                        c,
                                    ),
                                    assoc_rel(
                                        dc,
                                        assoc["commons_Deployment::target"],
                                        cn,
                                    ),
                                    assoc_rel(
                                        cn,
                                        assoc[
                                            "infrastructure_ComputingNode::ifaces"
                                        ],
                                        ni,
                                    ),
                                    assoc_rel(
                                        ni,
                                        assoc[
                                            "infrastructure_NetworkInterface::belongsTo"
                                        ],
                                        n,
                                    ),
                                ),
                            ),
                        ),
                    ),
                ),
            ),
        )
        solver.assert_and_track(assn, "software_package_iface_net")

        e1, e2, ni = Consts("e1 e2 i", elem_sort)
        assn = ForAll(
            [e1, e2, ni],
            Implies(
                And(
                    Or(
                        assoc_rel(
                            e1,
                            assoc["infrastructure_ComputingNode::ifaces"],
                            ni,
                        ),
                        assoc_rel(
                            e1, assoc["infrastructure_Storage::ifaces"], ni
                        ),
                    ),
                    Or(
                        assoc_rel(
                            e2,
                            assoc["infrastructure_ComputingNode::ifaces"],
                            ni,
                        ),
                        assoc_rel(
                            e2, assoc["infrastructure_Storage::ifaces"], ni
                        ),
                    ),
                ),
                e1 == e2,
            ),
        )
        solver.assert_and_track(assn, "iface_uniq")

        is_sat = solver.check()
        if is_sat == unsat:
            print("UNSAT!")
        stats = solver.statistics()
        return BenchmarkRes(
            time=stats.time,
            q_inst=stats.quant_instantiations,
            conflicts=stats.conflicts,
            memory=stats.memory,
        )
