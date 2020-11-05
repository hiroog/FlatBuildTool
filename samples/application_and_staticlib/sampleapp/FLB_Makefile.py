genv.SAMPLELIB_PATH= tool.findPath( '../samplelib' )
tool.execScript( '../DefaultSettings.py' )


src_list= [
    'SampleApp.cpp',
]

EXE_NAME= 'samplelib'

env= tool.createTargetEnvironment()

def makeExeName( env, src_file ):
    if src_file:
        return  env.tool.getGenericPath( env.getExeName( src_file + '_' + env.getTargetArch() + '_' + env.getConfig() ) )
    return  '.'
env.EXE_NAME_FUNC= makeExeName


env.addCCFlags( [ '-DENABLE_SAMPLE_LIB=1' ] )
env.addIncludePaths( [ os.path.join( genv.SAMPLELIB_PATH, 'include' ) ] )
env.addLibraries( ['samplelib'] )
env.refresh()

tool.addExeTasks( env, 'build', EXE_NAME, src_list, [ 'Debug', 'Release' ], env.getSupportArchList() )


tool.addCleanTask( env, 'clean' )

