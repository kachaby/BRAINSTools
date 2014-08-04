##- project(BRAINSInitializedControlPoints)
#-----------------------------------------------------------------------------
# Output directories.
#
###
include(CMakeBRAINS3BuildMacros)

set(ALL_PROGS_LIST
  BRAINSInitializedControlPoints
  )
foreach(prog ${ALL_PROGS_LIST})
  StandardBRAINSBuildMacro(NAME ${prog} TARGET_LIBRARIES BRAINSCommonLib )
endforeach()

