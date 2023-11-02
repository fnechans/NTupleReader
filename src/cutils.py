import ROOT

# Decorator to track time per function
# for performance measurements 
import time
import functools
def timer(func):
    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start = time.perf_counter()
        ret = func(*args, **kwargs)
        end = time.perf_counter()
        print(f"{func.__name__} took {(end-start):0.4f} s")
        return ret
    return wrapper


# Modify TFile to work with "with as" functionality
# This should be obsolete for next ROOT version (6.27?)
# since it is already on master
def _enter(self):
    return self
def _exit(self, exc_type, exc_val, exc_tb):
    self.Close()

def init_root():
    # this is to supress ROOT garbage collector for histograms
    ROOT.TH1.AddDirectory(False)
    # this is to stop ROOT from displaying plots when running
    ROOT.gROOT.SetBatch(True)
    # set atlas style for figures
    ROOT.gROOT.SetStyle('ATLAS')
    # enable MT for dataframe
    ROOT.EnableImplicitMT()

    # Add the enter/exit functions to TFile
    ROOT.TFile.__enter__ = _enter
    ROOT.TFile.__exit__ = _exit


# helper function for binning
def binner(size, low, high):
    step = (high-low)/size
    out = []
    for i in range(size):
        out.append(low+i*step)
    out.append(high)
    return out

def list_to_RVecF(list):
    list_str = ", ".join([str(f) for f in list])
    return f"ROOT::RVecF{{{list_str}}}"

if not ROOT.gInterpreter.Declare("""
    int getBin(const ROOT::RVecF& bins, double value)
    {
        for(int i=0; i < bins.size()-1; i++)
        {
           if(bins[i] < value && value < bins[i+1]){return i;}
        }
        return -99999;
    }
"""):
    raise RuntimeError("Failed to load getBin function")

if not ROOT.gInterpreter.Declare("""
#include <TH1.h>
#include <exception>

class Weighter
{
public:
  // Constructor, either based on histogram or file/path name
  Weighter(TH1D *h) : hprob(h) {}
  Weighter(Weighter &other) : hprob(other.hprob) {}
  Weighter(TString flName, TString hName)
  {
    fl = new TFile(flName, "READONLY");
    if(!fl || fl->IsZombie()) throw std::invalid_argument("Following file does not exist: "+flName);
    hprob = (TH1*)fl->Get(hName);
    fl->Close();
    delete fl;
  }

  // Main method, making the class call-able
  double operator()(double x, double y=0, double z=0) {
     int ibin = hprob->FindFixBin(x, y, z);
     return hprob->GetBinContent(ibin);
  }

private: 
  TH1* hprob;
  TFile* fl{nullptr};
};
"""):
    raise RuntimeError("Failed to load weighter class")
