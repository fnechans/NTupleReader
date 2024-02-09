from typing import List
from .cutils import list_to_RVecF


class Binning:
    """Holds information about binnning of 1D histogram.
    Most improtantly creates ROOT.RVecF from binning list
    which is compatible with RDataframe.

    Arguments:
        name (``str``): name of the histogram
        title (``str``): title of the histogram
        binning (``list``): binning of the histogram
    """

    def __init__(self, name: str, title: str, bin_edges: List[float]) -> None:
        self.name = name
        self.title = title
        self.bin_edges = bin_edges
        self.binning_str = list_to_RVecF(bin_edges)
