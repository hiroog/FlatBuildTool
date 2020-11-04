# simple makefile for multi platform

env= tool.createTargetEnvironment()
task= tool.addExeTask( env, 'test', [ 'main.cpp' ] )


tool.addNamedTask( genv, 'build', [task] ) # default task


tool.addCleanTask( genv, 'clean' ) # clean task


