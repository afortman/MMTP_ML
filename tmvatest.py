from ROOT import TMVA, TFile, TTree, TCut, TString
TMVA.Tools.Instance()

##https://nbviewer.jupyter.org/github/iml-wg/tmvatutorials/blob/master/TMVA_DNN.ipynb
##https://aholzner.wordpress.com/2011/08/27/a-tmva-example-in-pyroot/
##https://root.cern.ch/download/doc/tmva/TMVAUsersGuide.pdf

inputFile_sig = TFile.Open("bigfiles/hazel_sig_smearf.root")
inputFile_bkg = TFile.Open("bigfiles/hazel_bkg_smearf.root")
outputFile = TFile.Open("TMVAOutput_1M_smearf.root", "RECREATE")

factory = TMVA.Factory("TMVAClassification", outputFile,
                       "!V:!Silent:Color:DrawProgressBar:AnalysisType=Classification" )

loader = TMVA.DataLoader("dataset")

#loader.AddVariable("EventNumHazel",'I')
#loader.AddVariable("EventNumGingko",'I')
#loader.AddVariable("trigger_gingko",'I')
#loader.AddVariable("iroad_x",'I')
#loader.AddVariable("iroad_u",'I')
#loader.AddVariable("iroad_v",'I')
loader.AddVariable("Hit_plane0",'I')
loader.AddVariable("Hit_plane1",'I')
loader.AddVariable("Hit_plane2",'I')
loader.AddVariable("Hit_plane3",'I')
loader.AddVariable("Hit_plane4",'I')
loader.AddVariable("Hit_plane5",'I')
loader.AddVariable("Hit_plane6",'I')
loader.AddVariable("Hit_plane7",'I')
loader.AddVariable("Hit_n",'I')
#loader.AddVariable("dtheta")
#loader.AddVariable("chi2")

tsignal = inputFile_sig.Get("hazel")
tbackground = inputFile_bkg.Get("hazel")

loader.AddSignalTree(tsignal)
loader.AddBackgroundTree(tbackground)
#loader.PrepareTrainingAndTestTree(TCut(""),"nTrain_Signal=1000:nTrain_Background=1000:SplitMode=Random:NormMode=NumEvents:!V")
loader.PrepareTrainingAndTestTree(TCut(""),"SplitMode=Random:NormMode=NumEvents:!V")

# General layout
layoutString = TString("Layout=TANH|128,TANH|128,TANH|128,LINEAR");

# Training strategies
training0 = TString("LearningRate=1e-1,Momentum=0.9,Repetitions=1,"
                    "ConvergenceSteps=2,BatchSize=256,TestRepetitions=10,"
                    "WeightDecay=1e-4,Regularization=L2,"
                    "DropConfig=0.0+0.5+0.5+0.5, Multithreading=True")
training1 = TString("LearningRate=1e-2,Momentum=0.9,Repetitions=1,"
                    "ConvergenceSteps=2,BatchSize=256,TestRepetitions=10,"
                    "WeightDecay=1e-4,Regularization=L2,"
                    "DropConfig=0.0+0.0+0.0+0.0, Multithreading=True")
trainingStrategyString = TString("TrainingStrategy=")
trainingStrategyString += training0 + TString("|") + training1

# General Options
dnnOptions = TString("!H:!V:ErrorStrategy=CROSSENTROPY:VarTransform=N:"
                     "WeightInitialization=XAVIERUNIFORM")
dnnOptions.Append(":")
dnnOptions.Append(layoutString)
dnnOptions.Append(":")
dnnOptions.Append(trainingStrategyString)

# Standard implementation, no dependencies.
stdOptions =  dnnOptions + ":Architecture=CPU"
factory.BookMethod(loader, TMVA.Types.kDNN, "DNN_1M_smearf", stdOptions)

##Boosted Decision Trees
factory.BookMethod(loader,TMVA.Types.kBDT, "BDT_1M_smearf","!V:NTrees=200:MinNodeSize=2.5%:MaxDepth=2:BoostType=AdaBoost:AdaBoostBeta=0.5:UseBaggedBoost:BaggedSampleFraction=0.5:SeparationType=GiniIndex:nCuts=20" )

##Multi-Layer Perceptron (Neural Network)
factory.BookMethod(loader, TMVA.Types.kMLP, "MLP_1M_smearf","!H:!V:NeuronType=tanh:VarTransform=N:NCycles=100:HiddenLayers=N+5:TestRate=5:!UseRegulator" )

# CPU implementation, using BLAS
#cpuOptions = dnnOptions + ":Architecture=CPU"
#factory.BookMethod(loader, TMVA.Types.kDNN, "DNN CPU", cpuOptions)

factory.TrainAllMethods()

factory.TestAllMethods()
factory.EvaluateAllMethods()

c = factory.GetROCCurve(loader)
c.Draw()
c.SaveAs("roc/roc_TMVA_hits_smearf_1M.pdf")
