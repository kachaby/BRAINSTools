#! /usr/bin/env python

## \author Ali Ghayoor
##
## Main workflow for DWI data processing
## This workflow calls 4 other WFs for:
## -Correction and Alignement
## -CS (CompressSensing)
## -Estimation of RISs and ukfTracts
## -Statistic measurements

"""
DWIWorkFlow.py
==============

The purpose of this pipeline is to complete all the pre-processing steps (succeptiblity artifact correction, t2 space alignement and compressed sensing) needed to turn diffusion-weighted images into set of Rotationally invarient scalar (RIS) images whose statistics will be measured over each region label.

Usage:
  DWIWorkFlow.py --inputDWIScan DWISCAN --inputT2Scan T2SCAN --inputBrainLabelsMapImage BLMImage --program_paths PROGRAM_PATHS --python_aux_paths PYTHON_AUX_PATHS --labelsConfigFile LABELS_CONFIG_FILE [--workflowCacheDir CACHEDIR] [--resultDir RESULTDIR]
  DWIWorkFlow.py -v | --version
  DWIWorkFlow.py -h | --help

Options:
  -h --help                                 Show this help and exit
  -v --version                              Print the version and exit
  --inputDWIScan DWISCAN                    Path to the input DWI scan for further processing
  --inputT2Scan T2SCAN                      Path to the input T2 scan
  --inputBrainLabelsMapImage BLMImage       Path to the input brain labels map image
  --program_paths PROGRAM_PATHS             Path to the directory where binary files are places
  --python_aux_paths PYTHON_AUX_PATHS       Path to the AutoWorkup directory
  --labelsConfigFile LABELS_CONFIG_FILE     Configuration file that defines region labels (.csv)
  --workflowCacheDir CACHEDIR               Base directory that cache outputs of workflow will be written to (default: ./)
  --resultDir RESULTDIR                     Outputs of dataSink will be written to a sub directory under the resultDir named by input scan sessionID (default: CACHEDIR)
"""

def runMainWorkflow(DWI_scan, T2_scan, labelMap_image, BASE_DIR, dataSink_DIR, PYTHON_AUX_PATHS, LABELS_CONFIG_FILE):
    print("Running the workflow ...")

    sessionID = os.path.basename(os.path.dirname(DWI_scan))
    subjectID = os.path.basename(os.path.dirname(os.path.dirname(DWI_scan)))
    siteID = os.path.basename(os.path.dirname(os.path.dirname(os.path.dirname(DWI_scan))))

    #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\
    ####### Workflow ###################
    WFname = 'DWIWorkflow_CACHE_' + sessionID
    DWIWorkflow = pe.Workflow(name=WFname)
    DWIWorkflow.base_dir = BASE_DIR

    inputsSpec = pe.Node(interface=IdentityInterface(fields=['T2Volume', 'DWIVolume','LabelMapVolume']),
                         name='inputsSpec')

    inputsSpec.inputs.DWIVolume = DWI_scan
    inputsSpec.inputs.T2Volume = T2_scan
    inputsSpec.inputs.LabelMapVolume = labelMap_image

    outputsSpec = pe.Node(interface=IdentityInterface(fields=['DWI_Corrected','DWI_Corrected_Aligned','DWI_Corrected_Aligned_CS','DWIBrainMask',
                                                              'tensor_image','FAImage','MDImage','RDImage','FrobeniusNormImage',
                                                              'Lambda1Image','Lambda2Image','Lambda3Image','ukfTracks',
                                                              'FA_stats','MD_stats','RD_stats','FrobeniusNorm_stats',
                                                              'Lambda1_stats','Lambda2_stats','Lambda3_stats']),
                          name='outputsSpec')

    correctionWFname = 'CorrectionWorkflow_CACHE_' + sessionID
    myCorrectionWF = CreateCorrectionWorkflow(correctionWFname)

    CSWFname = 'CompressedSensingWorkflow_CACHE_' + sessionID
    myCSWF = CreateCSWorkflow(CSWFname, PYTHON_AUX_PATHS)

    estimationWFname = 'EstimationWorkflow_CACHE_' + sessionID
    myEstimationWF = CreateEstimationWorkflow(estimationWFname)

    measurementWFname = 'MeasurementWorkflow_CACHE_' + sessionID
    myMeasurementWF = CreateMeasurementWorkflow(measurementWFname, LABELS_CONFIG_FILE)

    #Connect up the components into an integrated workflow.
    DWIWorkflow.connect([(inputsSpec,myCorrectionWF,[('T2Volume','inputsSpec.T2Volume'),
                                           ('DWIVolume','inputsSpec.DWIVolume'),
                                           ('LabelMapVolume','inputsSpec.LabelMapVolume'),
                                           ]),
                         (myCorrectionWF, myCSWF,[('outputsSpec.CorrectedDWI_in_T2Space','inputsSpec.DWI_Corrected_Aligned'),
                                                ('outputsSpec.DWIBrainMask','inputsSpec.DWIBrainMask'),
                                                ]),
                         (myCorrectionWF, myEstimationWF, [('outputsSpec.DWIBrainMask','inputsSpec.DWIBrainMask')]),
                         (myCSWF, myEstimationWF, [('outputsSpec.DWI_Corrected_Aligned_CS','inputsSpec.DWI_Corrected_Aligned_CS')]),
                         (inputsSpec, myMeasurementWF, [('LabelMapVolume','inputsSpec.T2LabelMapVolume')]),
                         (myCorrectionWF, myMeasurementWF, [('outputsSpec.DWIBrainMask','inputsSpec.DWIBrainMask')]),
                         (myEstimationWF, myMeasurementWF, [('outputsSpec.FAImage','inputsSpec.FAImage'),
                                                            ('outputsSpec.MDImage','inputsSpec.MDImage'),
                                                            ('outputsSpec.RDImage','inputsSpec.RDImage'),
                                                            ('outputsSpec.FrobeniusNormImage','inputsSpec.FrobeniusNormImage'),
                                                            ('outputsSpec.Lambda1Image','inputsSpec.Lambda1Image'),
                                                            ('outputsSpec.Lambda2Image','inputsSpec.Lambda2Image'),
                                                            ('outputsSpec.Lambda3Image','inputsSpec.Lambda3Image')]),
                         (myCorrectionWF, outputsSpec, [('outputsSpec.CorrectedDWI','DWI_Corrected'),
                                                        ('outputsSpec.CorrectedDWI_in_T2Space','DWI_Corrected_Aligned'),
                                                        ('outputsSpec.DWIBrainMask','DWIBrainMask')]),
                         (myCSWF, outputsSpec, [('outputsSpec.DWI_Corrected_Aligned_CS','DWI_Corrected_Aligned_CS')]),
                         (myEstimationWF, outputsSpec, [('outputsSpec.tensor_image','tensor_image'),
                                                        ('outputsSpec.FAImage','FAImage'),
                                                        ('outputsSpec.MDImage','MDImage'),
                                                        ('outputsSpec.RDImage','RDImage'),
                                                        ('outputsSpec.FrobeniusNormImage','FrobeniusNormImage'),
                                                        ('outputsSpec.Lambda1Image','Lambda1Image'),
                                                        ('outputsSpec.Lambda2Image','Lambda2Image'),
                                                        ('outputsSpec.Lambda3Image','Lambda3Image'),
                                                        ('outputsSpec.ukfTracks','ukfTracks')]),
                         (myMeasurementWF, outputsSpec, [('outputsSpec.FA_stats','FA_stats'),
                                                         ('outputsSpec.MD_stats','MD_stats'),
                                                         ('outputsSpec.RD_stats','RD_stats'),
                                                         ('outputsSpec.FrobeniusNorm_stats','FrobeniusNorm_stats'),
                                                         ('outputsSpec.Lambda1_stats','Lambda1_stats'),
                                                         ('outputsSpec.Lambda2_stats','Lambda2_stats'),
                                                         ('outputsSpec.Lambda3_stats','Lambda3_stats')])
                       ])

    ## Write all outputs with DataSink
    DWIDataSink = pe.Node(interface=nio.DataSink(), name='DWIDataSink')
    DWIDataSink.inputs.base_directory = dataSink_DIR
    DWIDataSink.inputs.container = sessionID
    DWIDataSink.inputs.substitutions = [('_ComputeStatistics0', ''),('_ComputeStatistics1', ''),('_ComputeStatistics2', ''),
                                        ('_ComputeStatistics3', ''),('_ComputeStatistics4', ''),('_ComputeStatistics5', ''),('_ComputeStatistics6', '')]

    DWIWorkflow.connect(outputsSpec, 'DWI_Corrected', DWIDataSink, 'Outputs.@DWI_Corrected')
    DWIWorkflow.connect(outputsSpec, 'DWI_Corrected_Aligned', DWIDataSink, 'Outputs.@DWI_Corrected_Aligned')
    DWIWorkflow.connect(outputsSpec, 'DWI_Corrected_Aligned_CS', DWIDataSink, 'Outputs.@DWI_Corrected_Aligned_CS')
    DWIWorkflow.connect(outputsSpec, 'tensor_image', DWIDataSink, 'Outputs.@tensor_image')
    DWIWorkflow.connect(outputsSpec, 'DWIBrainMask', DWIDataSink, 'Outputs.@DWIBrainMask')
    DWIWorkflow.connect(outputsSpec, 'FAImage', DWIDataSink, 'Outputs.@FAImage')
    DWIWorkflow.connect(outputsSpec, 'MDImage', DWIDataSink, 'Outputs.@MDImage')
    DWIWorkflow.connect(outputsSpec, 'RDImage', DWIDataSink, 'Outputs.@RDImage')
    DWIWorkflow.connect(outputsSpec, 'FrobeniusNormImage', DWIDataSink, 'Outputs.@FrobeniusNormImage')
    DWIWorkflow.connect(outputsSpec, 'Lambda1Image', DWIDataSink, 'Outputs.@Lambda1Image')
    DWIWorkflow.connect(outputsSpec, 'Lambda2Image', DWIDataSink, 'Outputs.@Lambda2Image')
    DWIWorkflow.connect(outputsSpec, 'Lambda3Image', DWIDataSink, 'Outputs.@Lambda3Image')
    DWIWorkflow.connect(outputsSpec, 'ukfTracks', DWIDataSink, 'Outputs.@ukfTracks')
    DWIWorkflow.connect(outputsSpec, 'FA_stats', DWIDataSink, 'Outputs.@FA_stats')
    DWIWorkflow.connect(outputsSpec, 'MD_stats', DWIDataSink, 'Outputs.@MD_stats')
    DWIWorkflow.connect(outputsSpec, 'RD_stats', DWIDataSink, 'Outputs.@RD_stats')
    DWIWorkflow.connect(outputsSpec, 'FrobeniusNorm_stats', DWIDataSink, 'Outputs.@FrobeniusNorm_stats')
    DWIWorkflow.connect(outputsSpec, 'Lambda1_stats', DWIDataSink, 'Outputs.@Lambda1_stats')
    DWIWorkflow.connect(outputsSpec, 'Lambda2_stats', DWIDataSink, 'Outputs.@Lambda2_stats')
    DWIWorkflow.connect(outputsSpec, 'Lambda3_stats', DWIDataSink, 'Outputs.@Lambda3_stats')

    DWIWorkflow.write_graph()
    DWIWorkflow.run()


if __name__ == '__main__':
  import os
  import glob
  import sys

  from docopt import docopt
  argv = docopt(__doc__, version='1.0')
  print argv

  DWISCAN = argv['--inputDWIScan']
  assert os.path.exists(DWISCAN), "Input DWI scan is not found: %s" % DWISCAN

  T2SCAN = argv['--inputT2Scan']
  assert os.path.exists(T2SCAN), "Input T2 scan is not found: %s" % T2SCAN

  LabelMapImage = argv['--inputBrainLabelsMapImage']
  assert os.path.exists(LabelMapImage), "Input Brain labels map image is not found: %s" % LabelMapImage

  PROGRAM_PATHS = argv['--program_paths']

  PYTHON_AUX_PATHS = argv['--python_aux_paths']

  LABELS_CONFIG_FILE = argv['--labelsConfigFile']

  if argv['--workflowCacheDir'] == None:
      print("*** workflow cache directory is set to current working directory.")
      CACHEDIR = os.getcwd()
  else:
      CACHEDIR = argv['--workflowCacheDir']
      assert os.path.exists(CACHEDIR), "Cache directory is not found: %s" % CACHEDIR

  if argv['--resultDir'] == None:
      print("*** data sink result directory is set to the cache directory.")
      RESULTDIR = CACHEDIR
  else:
      RESULTDIR = argv['--resultDir']
      assert os.path.exists(RESULTDIR), "Results directory is not found: %s" % RESULTDIR

  print '=' * 100

  #\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/\/
  #####################################################################################
  #     Prepend the shell environment search paths
  PROGRAM_PATHS = PROGRAM_PATHS.split(':')
  PROGRAM_PATHS.extend(os.environ['PATH'].split(':'))
  os.environ['PATH'] = ':'.join(PROGRAM_PATHS)

  CUSTOM_ENVIRONMENT=dict()

  # Platform specific information
  #     Prepend the python search paths
  PYTHON_AUX_PATHS = PYTHON_AUX_PATHS.split(':')
  PYTHON_AUX_PATHS.extend(sys.path)
  sys.path = PYTHON_AUX_PATHS

  import SimpleITK as sitk
  import nipype
  from nipype.interfaces import ants
  from nipype.interfaces.base import CommandLine, CommandLineInputSpec, TraitedSpec, File, Directory
  from nipype.interfaces.base import traits, isdefined, BaseInterface
  from nipype.interfaces.utility import Merge, Split, Function, Rename, IdentityInterface
  import nipype.interfaces.io as nio   # Data i/oS
  import nipype.pipeline.engine as pe  # pypeline engine
  import nipype.interfaces.matlab as matlab
  from SEMTools import *
  #####################################################################################
  from CorrectionWorkflow import CreateCorrectionWorkflow
  from CSWorkflow import CreateCSWorkflow
  from EstimationWorkflow import CreateEstimationWorkflow
  from MeasurementWorkflow import CreateMeasurementWorkflow

  exit = runMainWorkflow(DWISCAN, T2SCAN, LabelMapImage, CACHEDIR, RESULTDIR, PYTHON_AUX_PATHS, LABELS_CONFIG_FILE)

  sys.exit(exit)
