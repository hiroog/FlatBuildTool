# build static library

src_list= [
    'function.cpp',
]

task_list= []


env= tool.createTargetEnvironment()
env.setTargetArch( 'x86' )
task_list.append( tool.addLibTask( env, 'test', src_list ) )


env= tool.createTargetEnvironment()
env.setTargetArch( 'x64' )
task_list.append( tool.addLibTask( env, 'test', src_list ) )


tool.addNamedTask( genv, 'build', task_list )


