##- project(BRAINSABC)

#   TBB_ROOT - (as a CMake or environment variable)
#               The root directory of the TBB implementation found
#   FIND_LIBRARY_USE_LIB64_PATHS - Global property that controls whether findTBB should search for
set(FIND_LIBRARY_USE_LIB64_PATHS ON)
find_package(TBB REQUIRED)

message(STATUS "TBB_ROOT: ${TBB_ROOT}")
message(STATUS "TBB_INCLUDE_DIRS: ${TBB_INCLUDE_DIRS}")
message(STATUS "TBB_LIBRARY: ${TBB_LIBRARY}")


#-----------------------------------------------------------------------------
# Dependencies.
#

#
# ITK
#
FindITKUtil(BRAINSABC_ITK
  ITKAnisotropicSmoothing
  ITKDistanceMap
  ITKOptimizersv4
  ITKMetricsv4
  ITKRegistrationMethodsv4
  ITKRegionGrowing
  ITKBinaryMathematicalMorphology
  ITKConnectedComponents
  ITKCurvatureFlow
  ITKImageFilterBase
  ITKImageFunction
  ITKImageGrid
  ITKImageIntensity
  ITKImageStatistics
  ITKMathematicalMorphology
  ITKRegistrationCommon
  ITKSmoothing
  ITKStatistics
  ITKTestKernel
  ITKThresholding
  ITKTransform
  ITKImageCompare)

#-----------------------------------------------------------------------------
# Output directories.
#

###
add_subdirectory(brainseg)

if(BUILD_TESTING AND NOT Slicer_BUILD_BRAINSTOOLS)
  add_subdirectory(TestSuite)
endif()

