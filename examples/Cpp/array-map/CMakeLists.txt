cmake_minimum_required(VERSION 2.8)
project (CppExample3)

set(PROJECT_ROOT_DIR ${CMAKE_SOURCE_DIR})
set(COMMON_SRC_DIR ${PROJECT_ROOT_DIR}/../common-src)

if(MSVC)
  add_definitions (-wd4146 -wd4800)
endif()


if (WIN32)
  add_definitions(
    -D_WIN32_WINNT=0x0601 
    -DWIN32_LEAN_AND_MEAN 
    -D _CRT_SECURE_NO_WARNINGS
    -D_SCL_SECURE_NO_WARNINGS 
    -DNOMINMAX
    )
endif()

include_directories(${PROJECT_ROOT_DIR}/src)
include_directories(${COMMON_SRC_DIR})

set(ALL_SRC_FILES 
    ${PROJECT_ROOT_DIR}/src/main.cpp
    ${PROJECT_ROOT_DIR}/src/AutogenConfig.h
    ${PROJECT_ROOT_DIR}/src/AutogenConfig.cpp
    ${COMMON_SRC_DIR}/Utility/Conv.h
    ${COMMON_SRC_DIR}/Utility/Conv.cpp
    ${COMMON_SRC_DIR}/Utility/Logging.h
    ${COMMON_SRC_DIR}/Utility/Logging.cpp
    ${COMMON_SRC_DIR}/Utility/Portability.h
    ${COMMON_SRC_DIR}/Utility/Preprocessor.h
    ${COMMON_SRC_DIR}/Utility/Range.cpp
    ${COMMON_SRC_DIR}/Utility/Range.h
    ${COMMON_SRC_DIR}/Utility/ScopeGuard.h
    ${COMMON_SRC_DIR}/Utility/SparseByteSet.h
    ${COMMON_SRC_DIR}/Utility/Traits.h
    ${COMMON_SRC_DIR}/Utility/UncaughtException.h
    ${COMMON_SRC_DIR}/Utility/StringUtil.h
    ${COMMON_SRC_DIR}/Utility/StringUtil.cpp
    ${COMMON_SRC_DIR}/Utility/WinUtil.h
    ${COMMON_SRC_DIR}/Utility/WinUtil.cpp
    )

    
add_executable(CppExample3 ${ALL_SRC_FILES})