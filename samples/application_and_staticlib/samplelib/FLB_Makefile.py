genv.SAMPLELIB_PATH= tool.findPath( '.' )
tool.execScript( '../DefaultSettings.py' )


src_list= [
    'src/SampleLib.cpp',
]

LIB_NAME= 'samplelib'


env= tool.createTargetEnvironment()
env.setLibDir( 'lib' )
env.addCCFlags( [ '-DENABLE_SAMPLE_LIB=1' ] )
env.addIncludePaths( [ os.path.join( genv.SAMPLELIB_PATH, 'include' ) ] )
env.refresh()

tool.addLibTasks( env, 'build', LIB_NAME, src_list, [ 'Debug', 'Release' ], env.getSupportArchList() )


def clean_files( task ):
    import BuildUtility
    BuildUtility.RemoveTree( os.path.join( task.cwd, 'obj' ) )
    BuildUtility.RemoveTree( os.path.join( task.cwd, 'lib' ) )

clean_task= tool.addScriptTask( genv, 'clean', clean_files )
clean_task.cwd= os.path.abspath( os.getcwd() )
