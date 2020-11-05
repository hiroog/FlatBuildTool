env= tool.createTargetEnvironment()

task= tool.addExeTask( env, 'test', [ 'main.cpp' ] )
tool.addTask( 'build', task )  # default task


tool.addCleanTask( genv, 'clean' ) # clean task


