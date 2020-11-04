genv.SAMPLELIB_PATH= tool.findPath( '.' )
tool.execScript( '../DefaultSettings.py' )


src_list= [
    'src/SampleLib.cpp',
]

LIB_NAME= 'samplelib'


env= tool.createTargetEnvironment()
env.setLibDir( 'lib' )
env.setDllDir( 'lib' )
env.addCCFlags( [ '-DENABLE_SAMPLE_LIB=1' ] )
env.addIncludePaths( [ os.path.join( genv.SAMPLELIB_PATH, 'include' ) ] )
env.refresh()

all_task= tool.addLibTasks( env, 'all', LIB_NAME, src_list, [ 'Debug', 'Release' ], env.getSupportArchList() )
tool.addNamedTask( env, 'build', [ all_task ] )


tool.addCleanTask( env, 'clean' )

