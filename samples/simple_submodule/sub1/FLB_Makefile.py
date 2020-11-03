
env= tool.createTargetEnvironment()

task= tool.addExeTask( env, 'test1', [ 'main.cpp' ] )

tool.addNamedTask( genv, 'build', [ task ] )




