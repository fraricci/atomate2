"""Jobs used in the calculation of elastic tensors."""

from __future__ import annotations

import logging
from dataclasses import dataclass, field
from pathlib import Path

import numpy as np
from jobflow import Flow, Response, job
from pymatgen.core.structure import Structure
from pymatgen.symmetry.analyzer import SpacegroupAnalyzer
from pymatgen.analysis.ferroelectricity.polarization import (
    EnergyTrend,
    Polarization,
    get_total_ionic_dipole,
)

from atomate2 import SETTINGS
from atomate2.common.schemas.ferroelectric import PolarizationDocument

logger = logging.getLogger(__name__)

__all__ = ["polarization_analysis"]

@job(output_schema=PolarizationDocument)
def polarization_analysis(lcalcpol_outputs):
    """
    Recovers the same branch polarization and spontaneous polarization
    for a ferroelectric workflow.
    """

    # ferroelectric workflow groups calculations by generated wfid tag
    polarization_tasks = reversed(lcalcpol_outputs.values())

    tasks = []
    outcars = []
    structure_dicts = []
    sort_weight = []
    energies_per_atom = []
    energies = []
    zval_dicts = []

    for p in polarization_tasks:
        # Grab data from each polarization task
        energies_per_atom.append(
            p["calcs_reversed"][0]["output"]["energy_per_atom"]
        )
        energies.append(p["calcs_reversed"][0]["output"]["energy"])
        tasks.append(p["task_label"])
        outcars.append(p["calcs_reversed"][0]["output"]["outcar"])
        structure_dicts.append(p["calcs_reversed"][0]["input"]["structure"])
        zval_dicts.append(p["calcs_reversed"][0]["output"]["outcar"]["zval_dict"])


    structures = [Structure.from_dict(structure) for structure in structure_dicts]

    # If LCALCPOL = True then Outcar will parse and store the pseudopotential zvals.
    zval_dict = zval_dicts.pop()

    # Assumes that we want to calculate the ionic contribution to the dipole moment.
    # VASP's ionic contribution is sometimes strange.
    # See pymatgen.analysis.ferroelectricity.polarization.Polarization for details.
    p_elecs = [outcar["p_elec"] for outcar in outcars]
    p_ions = [
        get_total_ionic_dipole(structure, zval_dict) for structure in structures
    ]

    polarization = Polarization(p_elecs, p_ions, structures)

    p_change = np.ravel(polarization.get_polarization_change()).tolist()
    p_norm = polarization.get_polarization_change_norm()
    polarization_max_spline_jumps = polarization.max_spline_jumps()
    same_branch = polarization.get_same_branch_polarization_data(
        convert_to_muC_per_cm2=True
    )
    raw_elecs, raw_ions = polarization.get_pelecs_and_pions()
    quanta = polarization.get_lattice_quanta(convert_to_muC_per_cm2=True)

    energy_trend = EnergyTrend(energies_per_atom)
    energy_max_spline_jumps = energy_trend.max_spline_jump()

    polarization_dict = {}

    def split_abc(var, var_name):
        d = {}
        for i, j in enumerate("abc"):
            d.update({var_name + f"_{j}": np.ravel(var[:, i]).tolist()})
        return d

    # General information
    polarization_dict.update(
        {"pretty_formula": structures[0].composition.reduced_formula}
    )
    polarization_dict.update({"wfid": wfid})
    polarization_dict.update({"task_label_order": tasks})

    # Polarization information
    polarization_dict.update({"polarization_change": p_change})
    polarization_dict.update({"polarization_change_norm": p_norm})
    polarization_dict.update(
        {"polarization_max_spline_jumps": polarization_max_spline_jumps}
    )
    polarization_dict.update(split_abc(same_branch, "same_branch_polarization"))
    polarization_dict.update(split_abc(raw_elecs, "raw_electron_polarization"))
    polarization_dict.update(split_abc(raw_ions, "raw_ion_polarization"))
    polarization_dict.update(split_abc(quanta, "polarization_quanta"))
    polarization_dict.update({"zval_dict": zval_dict})

    # Energy information
    polarization_dict.update(
        {"energy_per_atom_max_spline_jumps": energy_max_spline_jumps}
    )
    polarization_dict.update({"energies": energies})
    polarization_dict.update({"energies_per_atom": energies_per_atom})
    polarization_dict.update({"outcars": outcars})
    polarization_dict.update({"structures": structure_dicts})


    
    return PolarizationDocument(**polarization_dict)
