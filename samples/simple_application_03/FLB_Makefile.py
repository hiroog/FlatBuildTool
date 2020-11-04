# vim:ts=4 sw=4 et:

src_list= [
    'main.cpp',
    'subfile.cpp',
]


env= tool.createTargetEnvironment()
#------------------------------------------------------------------------------
# tool API
#------------------------------------------------------------------------------
# path= tool.getEnv( 'envname', default_value )
# path= tool.findPath( 'path-name', 'envname' )

# task= tool.findTask( 'task-name' )
# task= tool.addTask( 'task-name', task_obj )
# task= tool.removeTask( 'task-name' )

# tool.execScript( 'file_name.py' )
# tool.execSubmoduleScripts( 'file_name.py', module_list )
# tool.pushDir( module_name )
# tool.popDir()

# env= tool.createTargetEnvironment( platform_name )
# tool.addPlatform( platform_name, platform_env_class )


#------------------------------------------------------------------------------
# task API
#------------------------------------------------------------------------------
# task= tool.addLibTask( env, target_name, src_list )
# task= tool.addExeTask( env, target_name, src_list )
# task= tool.addDllTask( env, target_name, src_list )

# task= tool.addNamedTask( env, target_name, task_list )
# task= tool.addScriptTask( env, target_name, script )


#------------------------------------------------------------------------------
# default settings
#------------------------------------------------------------------------------
#env.addIncludePaths( [] )
#env.addCCFlags( [] )
#env.addLibPaths( [] )
#env.addLinkFlags( [] )
#env.addLibraries( [] )


#------------------------------------------------------------------------------
# custom output name
#------------------------------------------------------------------------------
def makeExeName( env, src_name ):
    if src_name:
        return  env.getExeName( src_name + '_' + env.getTargetArch() + '_' + env.getConfig() )
    return  '.'

env.EXE_NAME_FUNC= makeExeName


#------------------------------------------------------------------------------
# build params
#------------------------------------------------------------------------------
# env.getHostArch()
# env.getHostPlatform()
# env.getTargetArch()
# env.getTargetPlatform()
# env.getConfig()

# env.setConfig( config_name )
# env.setTargetArch( arch_name )
# env.setApiLevel( android_api_level )

# env.clone()
# env.refresh()


#------------------------------------------------------------------------------
# parallel config bulid
#------------------------------------------------------------------------------
task_list= []
for config in [ 'Release', 'Debug' ]:
    local_env= env.clone()
    local_env.setConfig( config )
    local_env.refresh()
    task_list.append( tool.addExeTask( local_env, 'test', src_list ) )

tool.addNamedTask( genv, 'build', task_list )


#------------------------------------------------------------------------------
# clean task
#------------------------------------------------------------------------------
tool.addCleanTask( genv, 'clean' )



