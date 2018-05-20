

env= tool.createTargetEnvironment()
task= tool.addExeTask( env, 'test', [ 'main.cpp' ] )


tool.addNamedTask( genv, 'build', [task] )


