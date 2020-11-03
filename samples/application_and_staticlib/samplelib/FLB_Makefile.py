
genv.SAMPLELIB_PATH= tool.findPath( '.' )
tool.execScript( '../DefaultSettings.py' )

genv.setLibDir( 'lib' )
genv.setDllDir( 'lib' )


src_list= [
    'src/SampleLib.cpp',
]

LIB_NAME= 'samplelib'


env= tool.createTargetEnvironment()
env.addCCFlags( [ '-DENABLE_SAMPLE_LIB=1' ] )


all= tool.addLibTasks( env, 'all', LIB_NAME, src_list, [ 'Debug', 'Release' ], env.getSupportArchList() )

tool.addNamedTask( env, 'build', [ all ] )

