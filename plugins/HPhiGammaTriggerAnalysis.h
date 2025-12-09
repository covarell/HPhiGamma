
//---------- class declaration----------

class HPhiGammaTriggerAnalysis : public edm::EDAnalyzer {
public:
  explicit HPhiGammaTriggerAnalysis(const edm::ParameterSet&);
  ~HPhiGammaTriggerAnalysis();

private:
  virtual void beginJob() override;
  virtual void analyze(const edm::Event&, const edm::EventSetup&);
  virtual void endJob() override;
 
 //test method
  //  int countPrimaryVertex(edm::Handle<std::vector<reco::Vertex > > slimmedPV);

  bool runningOnData_;
  const edm::InputTag packedPFCandidates_;
  const edm::InputTag slimmedMuons_; 
  const edm::InputTag slimmedPhotons_;
  const edm::InputTag pvCollection_;  
  const edm::InputTag bsCollection_;  
  const edm::InputTag PileupSrc_;
  const edm::InputTag prunedGenParticles_;

  
  edm::LumiReWeighting Lumiweights_;

  edm::Service<TFileService> fs;

  void create_trees();

  // ----------member data ---------------------------
  TH1F* h_Events;

  TH1F* h_pileup;

  //debug

  bool debug;
  bool verbose;

  //Counters
  int nPV;

  int nPhotonsChosen;
  int nPhotonsOverSelection;
  int _Nevents_processed;
  int _Nevents_isPhoton;
  int nHLTphotons;
  //TTree and TTree variables
  TTree *mytree;

  int run_number;

  float currentMuMuPt;
  float bestMuMuPt;
  float bestMuMuMass;
  float bestMuMuGammaMass;
  float ph_eT;
  float ph_eta;
  float ph_etaSC;
  float ph_phi;
  float ph_energy;
  float ph_iso_ChargedHadron;
  float ph_iso_NeutralHadron;
  float ph_iso_Photon;
  float ph_iso_eArho;
  bool is_photon_wp90;
  float eTphMax;
  
  bool isIsoMuTrigger;
  bool isPhotonTrigger;
  bool isPhoton35Trigger;
  bool isBestMuMu_Found;
  bool cand_photon_found;

  bool is_hltL1sBigORLooseIsoEGXXerIsoTauYYerdRMin0p3;
  bool is_hltEG35R9Id90HE10IsoMEcalIsoFilter;
  bool is_hltEG35R9Id90HE10IsoMHcalIsoFilter;
  bool is_hltEG35R9Id90HE10IsoMTrackIsoFilter;

  int genID;

//rho for isolation
  float rho_;

  //MC truth
  float PU_Weight;
  float MC_Weight;

  //Tokens
  edm::EDGetTokenT<std::vector<pat::PackedCandidate> > packedPFCandidatesToken_; 
  edm::EDGetTokenT<std::vector<pat::Muon> > slimmedMuonsToken_; 
  edm::EDGetTokenT<std::vector<reco::Vertex> > offlineSlimmedPrimaryVerticesToken_; 
  edm::EDGetTokenT<reco::BeamSpot> offlineBeamSpotToken_;
  edm::EDGetTokenT<std::vector<PileupSummaryInfo> > pileupSummaryToken_;
  edm::EDGetTokenT<GenEventInfoProduct> GenInfoToken_;
  edm::EDGetTokenT<edm::TriggerResults> triggerBitsToken_;
  edm::EDGetTokenT<std::vector<pat::TriggerObjectStandAlone> > triggerObjectsToken_;
  edm::EDGetTokenT<std::vector<reco::GenParticle>> prunedGenParticlesToken_;

  //Ele ID decisions objects
  edm::EDGetToken electronsMiniAODToken_;

  //Photon ID decisions
  edm::EDGetToken photonsMiniAODToken_;

  //rho (PU energy density)
  edm::EDGetTokenT<double> rhoToken_;

  bool verboseIdFlag_;

  //Effective areas for isolation
  EffectiveAreas   effectiveAreas_el_;
  EffectiveAreas   effectiveAreas_ph_;

};
