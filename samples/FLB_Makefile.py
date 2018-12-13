
module_list= [ 't0', 't1', 'staticlib', 't3', 't4', 'submodule', 'include' ]

tool.execSubmoduleScripts( 'FLB_Makefile.py', module_list )

tool.addSubmoduleTasks( genv, 'build', module_list )



#tool.pushDir( 't0' )
#tool.execScript( 'FLB_Makefile.py' )
#tool.popDir()
 
#tool.pushDir( 't1' )
#tool.execScript( 'FLB_Makefile.py' )
#tool.popDir()
 
#tool.pushDir( 't2' )
#tool.execScript( 'FLB_Makefile.py' )
#tool.popDir()
 
#tool.pushDir( 't3' )
#tool.execScript( 'FLB_Makefile.py' )
#tool.popDir()
 
#tool.pushDir( 't4' )
#tool.execScript( 'FLB_Makefile.py' )
#tool.popDir()
#
#
#
#tool.addNamedTask( genv, 'build', [
#                tool.findTask( 't0/build' ),
#                tool.findTask( 't1/build' ),
#                tool.findTask( 't2/build' ),
#                tool.findTask( 't3/build' ),
#                tool.findTask( 't4/build' ),
#            ] )

