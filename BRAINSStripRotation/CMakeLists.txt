project(BRAINSStripRotation)
include(CMakeBRAINS3BuildMacros)

set(prog BRAINSStripRotation)

StandardBRAINSBuildMacro( NAME ${prog} TARGET_LIBRARIES BRAINSCommonLib )
