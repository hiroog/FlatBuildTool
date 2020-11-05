module_list= [ 'sub1', 'sub2' ]

tool.execSubmoduleScripts( 'FLB_Makefile.py', module_list )

tool.addSubmoduleTasks( genv, 'clean', module_list )
tool.addSubmoduleTasks( genv, 'build', module_list )


#tool.list()
