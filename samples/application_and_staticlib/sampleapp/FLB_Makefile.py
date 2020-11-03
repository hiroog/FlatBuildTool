genv.SAMPLELIB_PATH= tool.findPath( '../samplelib' )
tool.execScript( '../DefaultSettings.py' )


src_list= [
    'SampleApp.cpp',
]

EXE_NAME= 'samplelib'


env= tool.createTargetEnvironment()
env.addCCFlags( [ '-DENABLE_SAMPLE_LIB=1' ] )


def makeExeName( env, src_file ):
    if src_file:
        return  env.tool.getGenericPath( env.getExeName( src_file + '_' + env.getTargetArch() + '_' + env.getConfig() ) )
    return  '.'

env.EXE_NAME_FUNC= makeExeName


all= tool.addExeTasks( env, 'all', EXE_NAME, src_list, [ 'Debug', 'Release' ], env.getSupportArchList() )

tool.addNamedTask( env, 'build', [ all ] )

