##- project(CleanUpOverlapLabels)

## Build all the programs
##
set(ALL_PROGS_LIST
  CleanUpOverlapLabels
  )
foreach( prog ${ALL_PROGS_LIST} )
  StandardBRAINSBuildMacro( NAME ${prog} TARGET_LIBRARIES BRAINSCommonLib )
endforeach()
