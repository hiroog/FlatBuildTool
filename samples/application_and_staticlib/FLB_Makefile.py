
module_list= [ 'samplelib', 'sampleapp' ]


tool.execSubmoduleScripts( 'FLB_Makefile.py', module_list )

tool.addSubmoduleTasks( genv, 'clean', module_list )

lib_task= tool.addSubmoduleTasks( genv, 'build_lib', ['samplelib'], 'build' )
app_task= tool.addSubmoduleTasks( genv, 'build_app', ['sampleapp'], 'build' )

lib_task.addCompleteTask( app_task )

tool.addNamedTask( genv, 'build', [lib_task] )


