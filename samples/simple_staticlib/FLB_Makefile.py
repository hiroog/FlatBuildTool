# static library

src_list= [
    'function.cpp',
]

task_list= []


env= tool.createTargetEnvironment()
env.setConfig( 'Debug' )
env.refresh()
task_list.append( tool.addLibTask( env, 'test', src_list ) )


env= tool.createTargetEnvironment()
env.setConfig( 'Release' )
env.refresh()
task_list.append( tool.addLibTask( env, 'test', src_list ) )


tool.addGroupTask( genv, 'build', task_list )

tool.addCleanTask( genv, 'clean' )

