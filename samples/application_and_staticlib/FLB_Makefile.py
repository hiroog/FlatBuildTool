# vim:ts=4 sw=4 et:

module_list= [ 'samplelib', 'sampleapp' ]

tool.execSubmoduleScripts( 'FLB_Makefile.py', module_list )

tool.addTask( 'build', tool.findTask( 'sampleapp/build' ) )

tool.addSubmoduleTasks( genv, 'clean', module_list )

