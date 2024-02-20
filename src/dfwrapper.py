import ROOT
from .cutils import timer
from typing import Dict, Any


class DFWrapper:
    """Wrapper around RDataFrame using class makes some things easier
    this class is general and exists just to simplify few things

    Arguments:
        _df (``ROOT.RDataFrame``): RDataFrame
    """

    def __init__(self, _df: ROOT.RDataFrame):
        self.df = _df
        self.df_orig = _df
        self.objects = {}
        self.regions = {}
        self.empty = True

    def custom_decorator(self, decorator: Any) -> None:
        """Allows to define external function which acts on RDataFrame.
        The function should take and return RDataFrame.

        Arguments:
            decorator (``Any``): function which acts on RDataFrame
        """
        self.df = decorator(self.df)

    def Define(self, name: str, definition: str) -> None:
        """Defines variable in the dataframe using
         RDataFrame.Define function

        Arguments:
            name (``str``): name of the variable
            definition (``str``): definition of the variable
        """
        self.df = self.df.Define(name, definition)

    def Filter(self, name: str, definition: str) -> None:
        """Filters dataframe using RDataFrame.Filter function.

        Arguments:
            name (``str``): name of the filter
            definition (``str``): definition of the filter
        """
        self.df = self.df.Filter(definition, name)

    def Count(self) -> int:
        """Returns number of entries in the dataframe."""
        return self.df.Count()

    def Range(self, entries: int) -> None:
        """Limits number of entries at current selection level."""
        self.df = self.df.Range(entries)

    def Region(self, name: str, definition: str = "") -> "DFWrapper":
        """Regions define different selections we want to look at.
        Each region is DFWrapper by itself and can be retrieved
        from the main DFWrapper through [] based on its `name`

        Arguments:
            name (``str``): name of the region
            definition (``str``): definition of the region

        Returns:
            ``DFWrapper``: new DFWrapper of the region
        """
        if name in self.regions.keys():
            raise RuntimeError(f"Region: Region with name {name} already exist")
        self.regions[name] = DFWrapper(self.df)
        if definition != "":
            self.regions[name].Filter(name, definition)
        return self.regions[name]

    def __getitem__(self, region: str) -> "DFWrapper":
        """Allows to access regions from the main DFWrapper.

        Arguments:
            region (``str``): name of the region

        Returns:
            ``DFWrapper``: DFWrapper of the region
        """
        if region not in self.regions.keys():
            raise RuntimeError(f"[]: Region with name {region} does not exist")
        return self.regions[region]

    def GetObj(self, name: str) -> ROOT.TObject:
        """Get object from the wrapper."""
        if name not in self.objects.keys():
            raise RuntimeError(f"GetObj: Object with name {name} does not exists")
        return self.objects[name]

    # booking functions
    def Book1D(
        self, name: str, model: ROOT.RDF.TH1DModel, variable: str, weight: str
    ) -> ROOT.TObject:
        """Book 1D histogram in the dataframe based on TH1DModel.

        Arguments:
            name (``str``): name of the histogram
            model (``ROOT.RDF.TH1DModel``): model of the histogram
            variable (``str``): variable of the histogram
            weight (``str``): weight of the histogram

        Returns:
            ``ROOT.TObject``: the histogram
        """
        if name in self.objects.keys():
            raise RuntimeError(f"Book1D: Object with name {name} already exists")

        self.empty = False

        self.objects[name] = self.df.Histo1D(model, variable, weight)

        return self.objects[name]

    def Book2D(
        self,
        name: str,
        model: ROOT.RDF.TH2DModel,
        variable: str,
        variable2: str,
        weight: str,
    ) -> ROOT.TObject:
        """Book 2D histogram in the dataframe based on TH2DModel.

        Arguments:
            name (``str``): name of the histogram
            model (``ROOT.RDF.TH2DModel``): model of the histogram
            variable (``str``): variable of the histogram on 1st axis
            variable2 (``str``): variable of the histogram on 2nd axis
            weight (``str``): weight of the histogram

        Returns:
            ``ROOT.TObject``: the histogram
        """
        if name in self.objects.keys():
            raise RuntimeError(f"Book2D: Object with name {name} already exists")

        self.empty = False

        self.objects[name] = self.df.Histo2D(model, variable, variable2, weight)

        return self.objects[name]

    def BookProf1D(self, name, title, binning, variable, variable2, weight):
        """Book 1D profile histogram in the dataframe.

        Arguments:
            name (``str``): name of the histogram
            title (``str``): title of the histogram
            binning (``list``): binning of the histogram
            variable (``str``): variable of the histogram on 1st axis
            variable2 (``str``): variable of the histogram on 2nd axis
            weight (``str``): weight of the histogram

        Returns:
            ``ROOT.TObject``: the histogram
        """
        if name in self.objects.keys():
            raise RuntimeError(f"BookProf1D: Object with name {name} already exists")

        self.empty = False

        self.objects[name] = self.df.Profile1D(
            (name, title, len(binning) - 1, binning), variable, variable2, weight
        )

        return self.objects[name]

    def WriteAll(self, writeDir):
        """Writes all objects, assumes externally opened file.
        Recursive through all regions.

        Arguments:
            writeDir (``ROOT.TDirectory``): directory to write
        """
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

    def WriteAllSuffix(self, writeDir, suffix=""):
        """Same as ``WriteAll``, but adds a suffix to the name of the
        objects instead of creating sub-directories per region."""
        writeDir.cd()
        for name, obj in self.objects.items():
            obj.Write(name + suffix)
        for name, region in self.regions.items():
            if region.empty:
                continue
            region.WriteAll(writeDir, f"{suffix}_{name}")

    def GetAll(self):
        """Get all objects recursively from all regions."""
        objects = list(self.objects.values())
        for region in self.regions.values():
            objects += list(region.GetAll())
        return objects

    def Cutflow(self):
        """Prints cutflow report."""
        allCutsReport = self.df_orig.Report()
        allCutsReport.Print()

    def Snapshot(self, treename, filename):
        """Saves dataframe to file:  https://root.cern.ch/doc/master/df007__snapshot_8py.html

        Arguments:
            treename (``str``): name of the tree
            filename (``str``): name of the file
        """
        if self.empty:
            return
        self.df.Snapshot(treename, filename)


@timer
def run_graphs(histos):
    """Run all graphs in the list."""
    ROOT.RDF.RunGraphs(histos)


@timer
def run_all(frames: Dict[str, DFWrapper], out_dir: str):
    """Run all frames in the list and writes output into a file.

    Arguments:
        frames (``dict``): dictionary of frames
        out_dir (``str``): output directory
    """
    print(frames)
    print("Running all frames")
    histos = []
    for frame in frames.values():
        histos += list(frame.GetAll())
    run_graphs(histos)
    print("Saving int file")
    for name, frame in frames.items():
        print(f"{name} #events final: ", frame.Count().GetValue())
        with ROOT.TFile(f"{out_dir}/histo_{name}.root", "RECREATE") as f:
            frame.WriteAll(f)
        frame.Cutflow()
