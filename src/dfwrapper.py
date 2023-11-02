import ROOT
from array import array
from .cutils import timer

# using class makes some things easier
# this class is general and exists just to
# simplify few things
class DFWrapper:
    def __init__(self, _df):
        self.df = _df
        self.df_orig = _df
        self.objects = {}
        self.regions = {}
        self.empty = True

    # this allows to define external function like _decorate_lxy
    # and easily to use on our new wrapper
    # so here, decorator is function, which shoudl take
    # and return RDataFrame
    def custom_decorator(self, decorator):
        self.df = decorator(self.df)

    # Functions directly from dataframe,
    # Avoids reassigment
    def Define(self, name, definition):
        self.df = self.df.Define(name, definition)

    def Filter(self, definition, name = ""):
        self.df = self.df.Filter(definition, name)

    def Count(self):
        return self.df.Count()
    
    def Range(self, entries):
        """Limits number of entries at curren selection level."""
        self.df = self.df.Range(entries)

    # Regions define different selections we want to apply
    # each region is DFWrapper by itself and get be getting
    # from the main DFWrapper through [] based on its `name`
    def Region(self, name, definition=""):
        if name in self.regions.keys():
            raise RuntimeError(f"Region: Region with name {name} already exist")
        self.regions[name] = DFWrapper(self.df)
        if definition != "":
            self.regions[name].Filter(definition, name)
        return self.regions[name]

    def __getitem__(self, region):
        if region not in self.regions.keys():
            raise RuntimeError(f"[]: Region with name {region} does not exist")
        return self.regions[region]

    # getters
    def GetObj(self, name):
        if name not in self.objects.keys():
            raise RuntimeError(f"GetObj: Object with name {name} does not exists")
        return self.objects[name]

    # booking functions
    def Book1D(self, name, model : ROOT.RDF.TH1DModel, variable : str, weight : str):
        if name in self.objects.keys():
            raise RuntimeError(f"Book1D: Object with name {name} already exists")

        self.empty = False

        self.objects[name] = self.df.Histo1D(
            model, variable, weight
        )

        return self.objects[name]

    def Book2D(self, name, model : ROOT.RDF.TH2DModel, variable, variable2, weight):
        if name in self.objects.keys():
            raise RuntimeError(f"Book2D: Object with name {name} already exists")

        self.empty = False

        self.objects[name] = self.df.Histo2D(
            model, variable, variable2, weight
        )

        return self.objects[name]

    def BookProf1D(self, name, title, binning, variable, variable2, weight):
        if name in self.objects.keys():
            raise RuntimeError(f"BookProf1D: Object with name {name} already exists")

        self.empty = False

        self.objects[name] = self.df.Profile1D(
            (name, title, len(binning)-1, binning),
            variable, variable2, weight
        )

        return self.objects[name]

    # Writes all objects, assumes externally opened file
    # Recursive through all regions
    def WriteAll(self, writeDir):
        writeDir.cd()
        for name, obj in self.objects.items():
            obj.Write(name)
        for name, region in self.regions.items():
            if region.empty:
                continue
            curDir = writeDir.GetDirectory(name)
            if not curDir:
                writeDir.mkdir(name)
                curDir = writeDir.GetDirectory(name)
            region.WriteAll(curDir)
    
    # Same but instead of subdir, regions as suffixes
    # (needed by some projects...)
    def WriteAllSuffix(self, writeDir, suffix = ""):
        writeDir.cd()
        for name, obj in self.objects.items():
            obj.Write(name+suffix)
        for name, region in self.regions.items():
            if region.empty:
                continue
            region.WriteAll(writeDir, f"{suffix}_{name}")
        

    def GetAll(self):
        objects = list(self.objects.values())
        for region in self.regions.values():
            objects += list(region.GetAll())
        return objects
    
    def Cutflow(self):
        allCutsReport = self.df_orig.Report()
        allCutsReport.Print()

    def Snapshot(self, treename, filename):
       # Saves dataframe to file:
       # https://root.cern.ch/doc/master/df007__snapshot_8py.html
       self.df.Snapshot(treename, filename)

@timer
def run_graphs(histos):
    ROOT.RDF.RunGraphs(histos)

@timer
def run_all(frames):
    print("Running all frames")
    histos = []
    for frame in frames.values():
        histos += list(frame.GetAll())
    run_graphs(histos)
    print("Saving int file")
    for name, frame in frames.items():
        print(f"{name} #events final: ", frame.Count().GetValue())
        with ROOT.TFile(f"histo_{name}.root","RECREATE") as f:
            frame.WriteAll(f)
        frame.Cutflow()