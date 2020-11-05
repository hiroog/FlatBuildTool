# vim:ts=4 sw=4 et:

src_list= [
    'main.cpp',
    'subfile.cpp',
]

env= tool.createTargetEnvironment()


#------------------------------------------------------------------------------
# parallel config bulid
#------------------------------------------------------------------------------
task_list= []
for config in [ 'Release', 'Debug' ]:
    local_env= env.clone()
    local_env.setConfig( config )
    local_env.refresh()
    # custom output name
    target= local_env.getExeName( 'test' + '_' + local_env.getTargetArch() + '_' + local_env.getConfig() )
    task_list.append( tool.addExeTask( local_env, src_list= src_list, target= target ) )

tool.addGroupTask( genv, 'build', task_list )


#------------------------------------------------------------------------------
# clean task
#------------------------------------------------------------------------------
tool.addCleanTask( genv, 'clean' )



