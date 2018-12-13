# change configuration
#  $ flmake clean
#  $ flmake

src_list= [
    'main.cpp',
    'subfile.cpp',
]


env= tool.createTargetEnvironment()
env.setConfig( 'Release' )
env.refresh()
task= tool.addExeTask( env, 'test', src_list )


tool.addNamedTask( genv, 'build', [task] )




def clean_files( env ):
    import BuildUtility
    BuildUtility.RemoveTree( 'obj' )

tool.addScriptTask( genv, 'clean', clean_files )



