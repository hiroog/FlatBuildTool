# custom bulid step

lib_src_list= [
    'function.cpp',
]

app_src_list= [
    'main.cpp',
]


env= tool.createTargetEnvironment()
if env.getTargetPlatform() == 'Windows':
    env.addCCFlags( [ '-DFLB_DLLEXPORT=__declspec(dllexport)' ] )
else:
    env.addCCFlags( [ '-DFLB_DLLEXPORT=' ] )
env.refresh()
lib_task= tool.addDllTask( env, 'testlib', lib_src_list )



env= tool.createTargetEnvironment()
if env.getTargetPlatform() == 'Windows':
    env.addCCFlags( [ '-DFLB_DLLEXPORT=__declspec(dllimport)' ] )
else:
    env.addCCFlags( [ '-DFLB_DLLEXPORT=' ] )
env.addLibraries( [ 'testlib' ] )
env.addLibPaths( [ env.getLibPath() ] )
env.refresh()
exe_task= tool.addExeTask( env, 'test', app_src_list )
lib_task.addCompleteTask( exe_task )



# custom copy task
def copy_func( task ):
    import BuildUtility
    src= os.path.join( task.cwd, 'lib', task.env.getTargetPlatform(), task.env.getTargetArch(), task.env.getConfig(), task.env.getDllName( 'testlib' ) )
    dest= os.path.join( task.cwd, 'obj', task.env.getTargetPlatform(), task.env.getTargetArch(), task.env.getConfig() )
    BuildUtility.CopyFilesDir( [ src ], dest )

copy_task= tool.addScriptTask( env, 'copy', copy_func )
copy_task.cwd= os.getcwd()
exe_task.addCompleteTask( copy_task )


tool.addNamedTask( genv, 'build', [lib_task] )



# custom clean task
def clean_files( task ):
    import BuildUtility
    BuildUtility.RemoveTree( os.path.join( task.cwd, 'obj' ) )
    BuildUtility.RemoveTree( os.path.join( task.cwd, 'lib' ) )

clean_task= tool.addScriptTask( genv, 'clean', clean_files )
clean_task.cwd= os.path.abspath( os.getcwd() )


