env= tool.createTargetEnvironment()

task= tool.addLibTask( env, 'test2', [ 'func2.cpp' ] )
tool.addTask( 'build', task )

tool.addCleanTask( genv, 'clean' )

