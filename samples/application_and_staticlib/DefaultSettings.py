# vim:ts=4 sw=4 et:

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
    return  env.tool.addGroupTask( env, task_name, task_list )

tool.addLibTasks= addLibTasks

#------------------------------------------------------------------------------

def addExeTasks( env, task_name, exe_name, src_list, config_list, arch_list ):
    task_list= []
    libpath= env.tool.global_env.SAMPLELIB_PATH
    for config in config_list:
        for arch in arch_list:
            depend_task= []
            local_env= env.clone()
            local_env.setConfig( config )
            local_env.setTargetArch( arch )
            lib_path= local_env.getOutputPath( os.path.join( libpath, 'lib' ) )
            local_env.addLibPaths( [lib_path] )
            #------------------------------------------------------------------
            lib_name= os.path.join( lib_path, local_env.getLibName( 'samplelib' ) )
            lib_task= env.tool.findTask( lib_name )
            if lib_task:
                depend_task.append( lib_task )
            #------------------------------------------------------------------
            local_env.refresh()
            target= local_env.getExeName( exe_name + '_' + local_env.getTargetArch() + '_' + local_env.getConfig() )
            task= env.tool.addExeTask( local_env, None, src_list, depend_task, target=target )
            task_list.append( task )
    return  env.tool.addGroupTask( env, task_name, task_list )

tool.addExeTasks= addExeTasks

#------------------------------------------------------------------------------

