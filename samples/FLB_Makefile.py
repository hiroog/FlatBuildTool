
module_list= [
	'simple_application_01',
	'simple_application_02',
	'simple_application_03',
	'simple_application_04',
	'simple_application_05',
	'simple_staticlib',
	'simple_submodule',
	'include_makefile' ]

tool.execSubmoduleScripts( 'FLB_Makefile.py', module_list )
tool.addSubmoduleTasks( genv, 'build', module_list )


