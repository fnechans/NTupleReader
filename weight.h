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
