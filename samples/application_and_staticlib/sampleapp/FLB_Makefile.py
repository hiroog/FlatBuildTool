genv.SAMPLELIB_PATH= tool.findPath( '../samplelib' )
tool.execScript( '../DefaultSettings.py' )


src_list= [
    'SampleApp.cpp',
]

env= tool.createTargetEnvironment()

env.addCCFlags( [ '-DENABLE_SAMPLE_LIB=1' ] )
env.addIncludePaths( [ os.path.join( genv.SAMPLELIB_PATH, 'include' ) ] )
env.addLibraries( ['samplelib'] )
env.refresh()

tool.addExeTasks( env, 'build', 'sampleapp', src_list, [ 'Debug', 'Release' ], env.getSupportArchList() )


tool.addCleanTask( env, 'clean' )

