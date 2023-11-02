import ROOT
from typing import List
from array import array

class H1DWrapper(object):
    """Holds information to define RDF Histo1D"""
    def __init__(self, name : str, title : str, binning : List[float], 
                 variable : str, weight : str):
        self.name = name
        self.model = ROOT.RDF.TH1DModel(
            name, title, len(binning)-1, array('d', binning)
        )
        self.variable = variable
        self.weight = weight

class H2DWrapper(object):
    """Holds information to define RDF Histo2D"""
    def __init__(self, name : str, title : str, binning1 : List[float],
                 binning2 : List[float], variable1 : str, variable2,
                 weight : str):
        self.name = name
        self.model = ROOT.RDF.TH2DModel(
            name, title, len(binning1)-1, array('d', binning1),
            len(binning2)-1, array('d', binning2)
        )
        self.variable1 = variable1
        self.variable2 = variable2
        self.weight = weight
