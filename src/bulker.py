from .dfwrapper import DFWrapper
from .histo import H1DWrapper, H2DWrapper
from typing import Dict, List

# Functions to do bulk of operations on DFWrapper from 
# a dict 

def BulkDefine(dfw : DFWrapper, dict : Dict[str, str]):
    for name, definition in dict.items():
        dfw.Define(name, definition)

def BulkBook1D(dfw : DFWrapper,  list : List[H1DWrapper]):
    for h1dw in list:
        dfw.Book1D(h1dw.name, h1dw.model, h1dw.variable, 
                   h1dw.weight)

def BulkBook2D(dfw : DFWrapper,  list : List[H2DWrapper]):
    for h2dw in list:
        dfw.Book2D(h2dw.name, h2dw.model, h2dw.variable1, 
                   h2dw.variable2, h2dw.weight)

