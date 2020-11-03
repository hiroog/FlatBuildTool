
module_list= [
	'include_makefile',
	'simple_application_01',
	'simple_application_02',
	'simple_application_03',
	'application_multiplatform',
	'simple_staticlib',
	'simple_submodule',
	'application_and_staticlib',
	'application_and_dynamiclib',
	]

tool.execSubmoduleScripts( 'FLB_Makefile.py', module_list )
tool.addSubmoduleTasks( genv, 'build', module_list )
tool.addSubmoduleTasks( genv, 'clean', module_list )


