# Debug/Release parallel bulid

src_list= [
    'main.cpp',
    'subfile.cpp',
]

task_list= []


env= tool.createTargetEnvironment()

# --- switch to debug build
env.setConfig( 'Debug' )
env.refresh()
task= tool.addExeTask( env, 'test', src_list )
task_list.append( task )


# --- switch to release build
env.setConfig( 'Release' )
env.refresh()
task= tool.addExeTask( env, 'test', src_list )
task_list.append( task )


# --- add build task
tool.addGroupTask( genv, 'build', task_list )


# --- add clean task
tool.addCleanTask( genv, 'clean' )



