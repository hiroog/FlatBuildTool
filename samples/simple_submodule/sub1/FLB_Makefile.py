env= tool.createTargetEnvironment()

task= tool.addExeTask( env, 'test1', [ 'main.cpp' ] )
tool.addTask( 'build', task )

tool.addCleanTask( genv, 'clean' )
