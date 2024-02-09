from Base import DFWrapper
from ROOT import RDataFrame

files = [
    "data1718_WZ_lowMu_repro_13TeV.root",
    "user.fballi.mc16_13TeV.P8B_A14_CTEQ6L1_bb_Jpsie3e13.STDM6.e8461_e7400_s3126_r10244_r10210_p5243_v00_outTree.root",
    "user.fballi.mc16_13TeV.P8B_A14_CTEQ6L1_bb_Jpsie3e3.STDM6.e8461_e7400_s3126_r10244_r10210_p5243_v00_outTree.root",
    "user.fballi.mc16_13TeV.P8B_A14_CTEQ6L1_bb_Jpsie3e8.STDM6.e8461_e7400_s3126_r10244_r10210_p5243_v00_outTree.root",
    "user.fballi.mc16_13TeV.P8B_A14_CTEQ6L1_Jpsie3e13.STDM6.e8461_e7400_s3126_r10244_r10210_p5243_v00_outTree.root",
    "user.fballi.mc16_13TeV.P8B_A14_CTEQ6L1_Jpsie3e3.STDM6.e8461_e7400_s3126_r10244_r10210_p5243_v00_outTree.root",
    "user.fballi.mc16_13TeV.P8B_A14_CTEQ6L1_Jpsie3e8.STDM6.e8461_e7400_s3126_r10244_r10210_p5243_v00_outTree.root",
]

for path in files:
    frame = DFWrapper(RDataFrame("MicroTree/microtree", "data/"+path))
    frame.Filter("presel", "isReco")
    frame.Snapshot("MicroTree/microtree", "data_skim/"+path)