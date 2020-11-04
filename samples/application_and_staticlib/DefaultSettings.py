
#------------------------------------------------------------------------------

def addLibTasks( env, task_name, lib_name, src_list, config_list, arch_list ):
    task_list= []
    for config in config_list:
        for arch in arch_list:
            local_env= env.clone()
            local_env.setConfig( config )
            local_env.setTargetArch( arch )
            local_env.refresh()
            task= env.tool.addLibTask( local_env, lib_name, src_list )
            task_list.append( task )
    return  env.tool.addNamedTask( env, task_name, task_list )

tool.addLibTasks= addLibTasks

#------------------------------------------------------------------------------

def addExeTasks( env, task_name, exe_name, src_list, config_list, arch_list ):
    task_list= []
    libpath= env.tool.global_env.SAMPLELIB_PATH
    for config in config_list:
        for arch in arch_list:
            local_env= env.clone()
            local_env.setConfig( config )
            local_env.setTargetArch( arch )
            local_env.addLibPaths( [local_env.getOutputPath( os.path.join( libpath, 'lib' ) )] )
            local_env.refresh()
            task= env.tool.addExeTask( local_env, exe_name, src_list )
            task_list.append( task )
    return  env.tool.addNamedTask( env, task_name, task_list )

tool.addExeTasks= addExeTasks

#------------------------------------------------------------------------------

