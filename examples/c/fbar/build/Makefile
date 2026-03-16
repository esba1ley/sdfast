# Makefile for fbar SDFast Example

PROBLEM_NAME := fbar

# Naming of files all dependent upon the problem name -- pattern set up by sdfast examples
EXECUTABLE := ${PROBLEM_NAME}c
MAIN_PROGRAM := ../${EXECUTABLE}.c
SDFAST_DYN_FILE := ../${PROBLEM_NAME}.sd

SDFAST_AUTOCODE_C_FILES := ${PROBLEM_NAME}_dyn.c ${PROBLEM_NAME}_sar.c sdlib.c
SDFAST_AUTOCODE_FILES := ${SDFAST_AUTOCODE_C_FILES} ${PROBLEM_NAME}_info
SDFAST_OBJECT_FILES := ${PROBLEM_NAME}_dyn.o ${PROBLEM_NAME}_sar.o sdlib.o


# For MacOS clang/llvm compiler... 
COMPILER_FLAGS := --std=c90 -Wno-implicit-function-declaration -Wno-deprecated-non-prototype


# Running make without a specified target builds executable program only.
.DEFAULT := ${EXECUTABLE}


# Executable Program Build
${EXECUTABLE}: ${MAIN_PROGRAM} ${SDFAST_OBJECT_FILES}
	cc -o ${EXECUTABLE} ${MAIN_PROGRAM} ${SDFAST_OBJECT_FILES} ${COMPILER_FLAGS}

.PHONY=exe
exe: ${EXECUTABLE}


# object files from SDFast Auto-code
${SDFAST_OBJECT_FILES}: ${SDFAST_AUTOCODE_C_FILES}
	cc -c ${SDFAST_AUTOCODE_C_FILES} ${COMPILER_FLAGS}

.PHONY=obj
obj: ${SDFAST_OBJECT_FILES}

# C Autocoded SDFast Dynamics Files
${SDFAST_AUTOCODE_FILES}: ${SDFAST_DYN_FILE}
	sdfast -lc -ge ${SDFAST_DYN_FILE}

.PHONY=autocode
autocode: ${SDFAST_AUTOCODE_FILES}

# Data from running executable (via STDOUT)
${PROBLEM_NAME}.dat: ${EXECUTABLE}
	./${EXECUTABLE} >> ${PROBLEM_NAME}.dat

.PHONY=run
run: ${PROBLEM_NAME}.dat

# Analysis script (plotting data)
${PROBLEM_NAME}_output.pdf: ${PROBLEM_NAME}.dat
	python ../analysis.py ${PROBLEM_NAME}.dat

.PHONY=.analysis
analysis: ${PROBLEM_NAME}_output.pdf


# Everything (including analysis)
.PHONY=all
all: ${PROBLEM_NAME}_output.pdf


# Cleanup Targets
.PHONY=clean
clean: clean-objects clean-autocode clean-executable clean-run-output clean-analysis

.PHONY=clean-objects
clean-objects:
	-rm *.o

.PHONY=clean-autocode
clean-autocode:
	-rm ${SDFAST_AUTOCODE_FILES}

.PHONY=clean-executable
clean-executable:
	-rm ${EXECUTABLE}

.PHONY=clean-run-output
clean-run-output:
	-rm ${PROBLEM_NAME}.dat

.PHONY=clean-analysis
clean-analysis:
	-rm ${PROBLEM_NAME}_output.pdf