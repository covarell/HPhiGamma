//ROOT includes
#include <TH1F.h>
#include <TFile.h>
#include <TLorentzVector.h>
#include <TTree.h>
#include "Math/VectorUtil.h"
#include <stdlib.h>

#include "CommonTools/UtilAlgos/interface/TFileService.h"
#include "DataFormats/HepMCCandidate/interface/GenParticle.h"
#include "FWCore/Framework/interface/EDAnalyzer.h"
#include "FWCore/Framework/interface/Frameworkfwd.h"
#include "FWCore/Framework/interface/Event.h"
#include "FWCore/Framework/interface/MakerMacros.h"
#include "FWCore/ParameterSet/interface/ParameterSet.h"
#include "FWCore/ServiceRegistry/interface/Service.h"
#include "FWCore/Common/interface/TriggerNames.h" 
 
#include "HRhoGammaAOD.h"
 
// constructors and destructor
HRhoGammaAOD::HRhoGammaAOD(const edm::ParameterSet& iConfig)
{
  genParticlesToken_ = consumes<std::vector<reco::GenParticle> >(edm::InputTag("genParticles"));

  create_trees();
}

HRhoGammaAOD::~HRhoGammaAOD()
{
}

// ------------ method called for each event  ------------
void HRhoGammaAOD::analyze(const edm::Event& iEvent, const edm::EventSetup& iSetup)
{
  edm::Handle<std::vector<reco::GenParticle>  > genParticles;
  iEvent.getByToken(genParticlesToken_, genParticles);

  event_number = iEvent.id().event();

  genH_m        = -10.;
  genMeson_m    = -10.;
  genMeson_eta  = -10.;
  genMeson_phi  = -10.;
  genMeson_pT   = -10.;
  genPhoton_eT  = -10.;
  genPhoton_eta = -10.;
  genPhoton_phi = -10.;
  PiplusPt      = -10.;
  Piplus_eta    = -10.;
  Piplus_phi    = -10.;
  PiminusPt     = -10.;
  Piminus_eta   = -10.;
  Piminus_phi   = -10.;
  theta_pol     = -10.;
  TLorentzVector mu[2];

  for(auto gen = genParticles->begin(); gen != genParticles->end(); ++gen){ //start of genParticles loop
    //if (gen->mother() && gen->mother()->mother() && (gen->pdgId() == 25 || gen->pdgId() ==  211 || gen->pdgId() ==  -211 || gen->pdgId() == 113)) std::cout<<"pdgID = "<<gen->pdgId()<<" (mother ID = "<<gen->mother()->pdgId()<<", grandmotherID = "<<gen->mother()->mother()->pdgId()<<")"<<std::endl;
    if( gen->pdgId() == 211  && gen->mother()->pdgId() == 113 && (gen->mother()->mother()->pdgId() == 25 || gen->mother()->mother()->mother()->pdgId() == 25))  Piplus_phi  = gen->phi(), Piplus_eta  = gen->eta(), PiplusPt  = gen->pt();
    if( gen->pdgId() == -211 && gen->mother()->pdgId() == 113 && (gen->mother()->mother()->pdgId() == 25 || gen->mother()->mother()->mother()->pdgId() == 25))  Piminus_phi = gen->phi(), Piminus_eta = gen->eta(), PiminusPt = gen->pt();
    if( gen->pdgId() == 113  && (gen->mother()->pdgId() == 25 || gen->mother()->mother()->pdgId() == 25)) genMeson_pT  = gen->pt(), genMeson_phi  = gen->phi(),  genMeson_eta = gen->eta(), genMeson_m = gen->mass();
    if( gen->pdgId() == 22   && gen->mother()->pdgId() == 25) genPhoton_eT = gen->pt(), genPhoton_phi = gen->phi(), genPhoton_eta = gen->eta();
    if( gen->pdgId() == 25) genH_m = gen->mass();
  
  
    //For the polarization reweighting
    if(gen->pdgId()== 211 && gen->mother()->pdgId()== 113) {
      if(gen->mother()->mother()->pdgId()== 25 || gen->mother()->mother()->mother()->pdgId()== 25){
        mu[1].SetPxPyPzE(gen->px(),gen->py(),
        gen->pz(),gen->energy());
        mu[0].SetPxPyPzE(gen->mother()->px(),gen->mother()->py(),
        gen->mother()->pz(),gen->mother()->energy());
        }
      }
    }

    TVector3 rhoBoost = mu[0].BoostVector();
    mu[1].Boost(- rhoBoost);
    theta_pol = mu[0].Vect().Angle(mu[1].Vect());
    //std::cout<<"theta_pol = "<<theta_pol<<std::endl;
   //end of genParticles loop 
    //if (  Piminus_phi == -10.) std::cout<<"not matched!!!"<<std::endl;
  mytree->Fill();
}

//*************************************************************//
//                                                             //
//---------------------- Create the tree ----------------------//
//                                                             //
//*************************************************************//

void HRhoGammaAOD::create_trees()
{
  mytree = fs->make<TTree>("mytree", "Tree containing gen info");

  mytree->Branch("event_number",&event_number);

  mytree->Branch("genH_m",&genH_m);
  mytree->Branch("genMeson_m",&genMeson_m);
  mytree->Branch("genMeson_eta",&genMeson_eta);
  mytree->Branch("genMeson_phi",&genMeson_phi);
  mytree->Branch("genMeson_pT",&genMeson_pT);
  mytree->Branch("genPhoton_eT",&genPhoton_eT);
  mytree->Branch("genPhoton_eta",&genPhoton_eta);
  mytree->Branch("genPhoton_phi",&genPhoton_phi);
  mytree->Branch("PiplusPt",&PiplusPt);
  mytree->Branch("Piplus_eta",&Piplus_eta);
  mytree->Branch("Piplus_phi",&Piplus_phi);
  mytree->Branch("PiminusPt",&PiminusPt);
  mytree->Branch("Piminus_eta",&Piminus_eta);
  mytree->Branch("Piminus_phi",&Piminus_phi);
  mytree->Branch("theta_pol",&theta_pol);

}

void HRhoGammaAOD::beginJob()
{
}

void HRhoGammaAOD::endJob() 
{
}

//define this as a plug-in
DEFINE_FWK_MODULE(HRhoGammaAOD);
