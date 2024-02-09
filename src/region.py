from .dfwrapper import DFWrapper
from .histo import H1DWrapper
from .binning import Binning
from typing import List, Any
import itertools as it
from .bulker import BulkBook1D


# used to setup region in DFWrapper
class RegionWrapper:
    """Helper class to setup regions in DFWrapper.

    Arguments:
        name (``str``): name of the region
        definition (``str``): definition of the region
    """

    def __init__(self, name: str, definition: str = ""):
        self.name = name
        self.definition = definition
        self.regions = {}

    def Region(self, region: "RegionWrapper"):
        """Adds sub-region to the region.

        Arguments:
            region (``RegionWrapper``): sub-region
        """
        new_name = self.name + "/" + region.name
        if new_name in self.regions.keys():
            raise RuntimeError(
                f"Region: Region with name {region.name} already exist in {self.name}"
            )
        self.regions[new_name] = region

    def Apply(self, df: DFWrapper, histos: List[H1DWrapper] = []):
        """Applies region to the dataframe and books histograms.

        Arguments:
            df (``DFWrapper``): dataframe
            histos (``List[H1DWrapper]``): list of histograms
        """
        df.Region(self.name, self.definition)
        BulkBook1D(df[self.name], histos)
        for _, region in self.regions.items():
            region.Apply(df[self.name], histos)


def add_regions_from_binnings(region: RegionWrapper, binnings: List[Binning]):
    """Defines regions from the list of binnings, resulting in one region
    per each combination of bins.

    Arguments:
        region (``RegionWrapper``): region wrapper to add regions to
        binnings (``List[Binning]``): list of binnings to create regions from
    """
    dim = len(binnings)
    bin_ranges = []
    for binning in binnings:
        # here -1 because number of bins is one smaller than
        # bin edges
        bin_ranges.append(range(0, len(binning.bin_edges) - 1))
    for bin_all in it.product(*bin_ranges):
        name = []
        selection = []
        for i in range(dim):
            name.append(f"{binnings[i].name}{bin_all[i]}")
            selection.append(
                f"{binnings[i].name} >= {binnings[i].bin_edges[bin_all[i]]} && "
                f"{binnings[i].name} < {binnings[i].bin_edges[bin_all[i]+1]}"
            )
        name = '_'.join(name)
        selection = ' && '.join(selection)
        region.Region(RegionWrapper(name, selection))
