"""Tools for calculating elastic tensors."""

import typing

if typing.TYPE_CHECKING:
    from typing import List, Tuple


def get_default_strain_states(order: int) -> List[Tuple[int, int, int, int, int, int]]:
    """
    Generate a list of strain-states for calculating 2nd or 3rd order elastic tensors.

    Parameters
    ----------
    order
        Order of the tensor expansion to be calculated. Can be either 2 or 3.

    Returns
    -------
    list[tuple[int, int, int, int, int, int]]
        A list of strain states.
    """
    if order == 2:
        return [
            (1, 0, 0, 0, 0, 0),
            (0, 1, 0, 0, 0, 0),
            (0, 0, 1, 0, 0, 0),
            (0, 0, 0, 2, 0, 0),
            (0, 0, 0, 0, 2, 0),
            (0, 0, 0, 0, 0, 2),
        ]

    if order == 3:
        return [
            (1, 0, 0, 0, 0, 0),
            (0, 1, 0, 0, 0, 0),
            (0, 0, 1, 0, 0, 0),
            (0, 0, 0, 2, 0, 0),
            (0, 0, 0, 0, 2, 0),
            (0, 0, 0, 0, 0, 2),
            (1, 1, 0, 0, 0, 0),
            (1, 0, 1, 0, 0, 0),
            (1, 0, 0, 2, 0, 0),
            (1, 0, 0, 0, 2, 0),
            (0, 1, 1, 0, 0, 0),
            (0, 0, 0, 2, 2, 0),
            (0, 0, 0, 2, 0, 2),
            (0, 0, 0, 0, 2, 2),
        ]

    raise ValueError(
        "only deformations for 2nd and 3rd order elastic tensors are supported."
    )
