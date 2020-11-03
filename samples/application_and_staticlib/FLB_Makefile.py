env= tool.createTargetEnvironment()

module_list= [ 'samplelib', 'sampleapp' ]

tool.execSubmoduleScripts( 'FLB_Makefile.py', module_list )

tool.addSubmoduleTasks( env, 'clean', module_list )

lib_task= tool.addSubmoduleTasks( env, 'build_lib', ['samplelib'], 'build' )
app_task= tool.addSubmoduleTasks( env, 'build_app', ['sampleapp'], 'build' )


lib_task.addCompleteTask( app_task )
tool.addNamedTask( env, 'build', [lib_task] )


