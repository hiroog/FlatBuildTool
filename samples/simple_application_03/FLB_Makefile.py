# vim:ts=4 sw=4 et:

src_list= [
    'main.cpp',
    'subfile.cpp',
]

env= tool.createTargetEnvironment()

#------------------------------------------------------------------------------
# custom output name
#------------------------------------------------------------------------------
def makeExeName( env, src_name ):
    if src_name:
        return  env.getExeName( src_name + '_' + env.getTargetArch() + '_' + env.getConfig() )
    return  '.'

env.EXE_NAME_FUNC= makeExeName


#------------------------------------------------------------------------------
# parallel config bulid
#------------------------------------------------------------------------------
task_list= []
for config in [ 'Release', 'Debug' ]:
    local_env= env.clone()
    local_env.setConfig( config )
    local_env.refresh()
    task_list.append( tool.addExeTask( local_env, 'test', src_list ) )

tool.addGroupTask( genv, 'build', task_list )


#------------------------------------------------------------------------------
# clean task
#------------------------------------------------------------------------------
tool.addCleanTask( genv, 'clean' )



