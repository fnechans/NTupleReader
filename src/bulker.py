from .dfwrapper import DFWrapper
from .histo import H1DWrapper, H2DWrapper
from typing import Dict, List, Any, Optional

# Functions to do bulk of operations on DFWrapper from
# a dict


def BulkDefine(dfw: DFWrapper, dict: Dict[str, Any]):
    """Define variables in the dataframe based on a dict

    Arguments:
        dfw (``DFWrapper``): target dataframe wrapper
        dict (``Dict[str, Any]``): dictionary of variable definitions
    """
    for name, definition in dict.items():
        dfw.Define(name, str(definition))


def BulkBook1D(
    dfw: DFWrapper, list: List[H1DWrapper], extra_weight: Optional[str] = None
):
    """Book 1D histograms in the dataframe based on a list of H1DWrappers.

    If extra_weight is not None, it will be multiplied with the weights in the H1DWrappers.

    Arguments:
        dfw (``DFWrapper``): target dataframe wrapper
        list (``List[H1DWrapper]``): list of H1DWrappers
        extra_weight (``Optional[str]``): optional weight
    """
    for h1dw in list:
        weight = (
            f'{extra_weight} * {h1dw.weight}'
            if extra_weight is not None
            else h1dw.weight
        )
        dfw.Book1D(h1dw.name, h1dw.model, h1dw.variable, weight)


def BulkBook2D(
    dfw: DFWrapper, list: List[H2DWrapper], extra_weight: Optional[str] = None
):
    """Book 2D histograms in the dataframe based on a list of H2DWrappers.

    If extra_weight is not None, it will be multiplied with the weights in the H2DWrappers.

    Arguments:
        dfw (``DFWrapper``): target dataframe wrapper
        list (``List[H2DWrapper]``): list of H2DWrappers
        extra_weight (``Optional[str]``): optional weight
    """
    for h2dw in list:
        weight = (
            f'{extra_weight} * {h2dw.weight}'
            if extra_weight is not None
            else h2dw.weight
        )
        dfw.Book2D(h2dw.name, h2dw.model, h2dw.variable1, h2dw.variable2, weight)
