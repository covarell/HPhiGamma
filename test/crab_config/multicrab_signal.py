from CRABAPI.RawCommand import crabCommand
from WMCore.Configuration import Configuration
from CRABClient.UserUtilities import config
config = Configuration()

config.section_('General')
config.General.transferOutputs = True

config.section_('JobType')
config.JobType.psetName = 'cmssw_config/run_HPhiGammaAnalysis.py'
config.JobType.pluginName = 'Analysis'
config.JobType.outputFiles = ['HPhiGammaAnalysis_output.root']
#config.JobType.outputFiles = ['LeptonMultiplicity_output.root']
config.JobType.allowUndistributedCMSSW = True #Otherwise get an error for incompatibility of architecture(slc7)/release(9_4_10). It is safe according to https://hypernews.cern.ch/HyperNews/CMS/get/computing-tools/4935/2.html

config.General.workArea = 'crab_projects/samples_MC/'
config.JobType.inputFiles = ['MCpileUp_2018_25ns_UltraLegacy_PoissonOOTPU.root','MyDataPileupHistogram.root'] #MC and data files for PileUp reweighting (2018)


config.section_('Data')
config.Data.inputDBS = 'global'
config.Data.splitting = 'Automatic'
#config.Data.splitting = 'LumiBased'
#config.Data.unitsPerJob = 5
config.Data.publication = False

config.section_('Site')
config.Site.storageSite = 'T2_IT_Legnaro'

if __name__ == '__main__':

    from CRABAPI.RawCommand import crabCommand
    from CRABClient.ClientExceptions import ClientException
    from httplib import HTTPException
    from multiprocessing import Process

    def submit(config):
        try:
            crabCommand('submit', config = config)
        except HTTPException as hte:
            print "Failed submitting task: %s" % (hte.headers)
        except ClientException as cle:
            print "Failed submitting task: %s" % (cle)

    #############################################################################################
    ## From now on that's what users should modify: this is the a-la-CRAB2 configuration part. ##
    #############################################################################################

    config.JobType.pyCfgParams = ['runningOnData=False'] # Configure 2018 MC signal jobs 

    config.General.requestName = 'HPhiGammaAnalysis_Signal_Phi_ggH'
    config.Data.inputDataset = '/GluGlu_HToPhiGamma_M125_TuneCP5_PSWeights_13TeV_powheg_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v3/MINIAODSIM'
    p = Process(target=submit, args=(config,))
    p.start()
    p.join()
    
    config.General.requestName = 'HPhiGammaAnalysis_Signal_Rho_ggH'
    config.Data.inputDataset = '/GluGlu_HToRhoGamma_M125_TuneCP5_PSWeights_13TeV_powheg_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v3/MINIAODSIM'
    p = Process(target=submit, args=(config,))
    p.start()
    p.join()
    '''
    config.General.requestName = 'HPhiGammaAnalysis_Signal_Phi_VBF'
    config.Data.inputDataset = '/VBF_HToPhiGamma_M125_TuneCP5_PSWeights_13TeV_powheg_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v1/MINIAODSIM'
    p = Process(target=submit, args=(config,))
    p.start()
    p.join()
    
    config.General.requestName = 'HPhiGammaAnalysis_Signal_Rho_VBF'
    config.Data.inputDataset = '/VBF_HToRhoGamma_M125_TuneCP5_PSWeights_13TeV_powheg_pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v3/MINIAODSIM'
    p = Process(target=submit, args=(config,))
    p.start()
    p.join()
    '''
    config.General.requestName = 'HPhiGammaAnalysis_Signal_K0s_ggH'
    config.Data.inputDataset = '/GluGluHtoK0starG_M-125_TuneCP5_PSWeights_13TeV_powheg-pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v2/MINIAODSIM'
    p = Process(target=submit, args=(config,))
    p.start()
    p.join()
    '''
    config.General.requestName = 'HPhiGammaAnalysis_Signal_K0s_VBF'
    config.Data.inputDataset = '/VBF_HtoK0starG_M-125_TuneCP5_PSWeights_13TeV_powheg-pythia8/RunIISummer20UL18MiniAODv2-106X_upgrade2018_realistic_v16_L1v1-v2/MINIAODSIM'
    p = Process(target=submit, args=(config,))
    p.start()
    p.join()
    
    #Just for trigger studies
    config.General.requestName = 'HPhiGammaL1TriggerAnalysis_DY10to50'
    config.Data.inputDataset = '/DYJetsToLL_M-10to50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer20UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v2/MINIAODSIM'
    p = Process(target=submit, args=(config,))
    p.start()
    p.join()

    config.General.requestName = 'HPhiGammaL1TriggerAnalysis_DY50' #Requires FileBased splitting
    config.Data.inputDataset = '/DYJetsToLL_M-50_TuneCP5_13TeV-madgraphMLM-pythia8/RunIISummer20UL18MiniAOD-106X_upgrade2018_realistic_v11_L1v1-v1/MINIAODSIM'
    p = Process(target=submit, args=(config,))
    p.start()
    p.join()
    '''