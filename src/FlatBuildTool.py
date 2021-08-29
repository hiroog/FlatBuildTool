# FlatBuildTool 2017/07/20 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  sys
import  time
import  Depend
import  JobQueue
import  BuildUtility
import  PlatformCommon
from BuildUtility import Log

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class BuildTool:

    def __init__( self, job_count= 0, option= None ):
        self.thread_pool= JobQueue.ThreadPool( job_count )
        self.timestamp_cache= Depend.TimeStampCache( self )
        self.source_cache= Depend.SourceFileCache( self )
        self.task_cache= Depend.TaskCache( self )
        self.global_env= PlatformCommon.TargetEnvironmentCommon( self )
        self.global_env.USER_OPTION= option
        self.platform_table= {}
        self.dir_stack= []
        self.result_code= 0

        #script_bin_path= os.path.dirname(__file__)
        script_bin_path= os.path.dirname(sys.argv[0])

        sys.path.append( script_bin_path )
        StartupScript= os.path.join( script_bin_path, 'FLB_Default.py' )

        if os.path.exists( StartupScript ):
            self.execScript( StartupScript )
        Log.v( option )

    def dump( self ):
        self.timestamp_cache.dump()
        self.source_cache.dump()
        self.task_cache.dump()

    #--------------------------------------------------------------------------

    def addPlatform( self, platform_name, platform_env ):
        Log.d( 'Load platform : ' + platform_name )
        self.platform_table[ platform_name ]= platform_env

    def createTargetEnvironment( self, platform= None, env= None ):
        if platform is None:
            platform= self.global_env.getHostPlatform()
        if env is None:
            env= self.global_env
        if platform in self.platform_table:
            return  self.platform_table[ platform ].TargetEnvironment( self, env )
        #raise BuildUtility.FLB_Error( 'platform "%s" not found' % platform )
        return  PlatformCommon.PlatformError( self )

    #--------------------------------------------------------------------------

    def execScript( self, file_name ):
        try:
            with open( file_name, 'r', encoding= 'UTF-8' ) as fi:
                script= fi.read()
                fi.close()
                exec( script, { 'os' : os, 'sys' : sys, 'Log' : Log, 'BuildUtility' : BuildUtility }, { 'tool' : self, 'genv' : self.global_env } )
        except FileNotFoundError:
            Log.e( 'Script "%s" not found' % file_name )
            raise


    def wait( self ):
        self.result_code= self.thread_pool.join()

    def getEnv( self, name, default_value= None ):
        if name in self.global_env.USER_OPTION:
            return  self.global_env.USER_OPTION[name]
        if name in os.environ:
            return  os.environ[name]
        return  default_value

    def findPath( self, path, env= None ):
        return  BuildUtility.FindPath2( path, self.getEnv( env ) if env else None )

    def findPaths( self, path_list ):
        return  BuildUtility.FindPaths( path )

    def getGenericPath( self, file ):
        #return  os.path.normpath( file )
        return  os.path.abspath( file )

    def pushDir( self, dir, prefix= None ):
        self.task_cache.addPrefix( prefix if prefix else dir )
        self.dir_stack.append( os.getcwd() )
        result=os.chdir( dir )
        #print( 'CHDIR RESULT=', dir, result, self.task_cache.getPrefix( 'DUMMY' ) )
        #print( os.getcwd() )

    def popDir( self ):
        os.chdir( self.dir_stack.pop() )
        self.task_cache.popPrefix()

    # run sub directorys script
    def execSubmoduleScripts( self, file_name, module_list ):
        for module in module_list:
            self.pushDir( module )
            self.execScript( file_name )
            self.popDir()

    #--------------------------------------------------------------------------

    def findTask( self, task_name ):
        return  self.task_cache.findTask( task_name )

    def addTask( self, task_name, task ):
        return  self.task_cache.addTask( task_name, task )

    def removeTask( self, task_name ):
        return  self.task_cache.removeTask( task_name )

    def addJob( self, job ):
        self.thread_pool.addJob( job )

    #--------------------------------------------------------------------------

    def addObjTask( self, env, target, src_list ):
        abs_target= self.getGenericPath( target )
        task= self.findTask( abs_target )
        if task != None:
            return  task

        abs_src_list= []
        task_list= []
        for src in src_list:
            abs_src= self.getGenericPath( src )
            abs_src_list.append( abs_src )
            task= self.findTask( abs_src )
            if task != None:
                task_list.append( task )

        command= env.getBuildCommand_CC( abs_target, abs_src_list )
        task= Depend.ObjTask( env, abs_target, abs_src_list, command )
        task.addDependTasks( task_list )
        self.addTask( abs_target, task )
        return  task


    def addExeTask( self, env, name= None, src_list= None, task_list= None, target=None ):
        if target is None:
            target= env.getExePath( name )
        abs_target= self.getGenericPath( target )
        task= self.findTask( abs_target )
        if task != None:
            return  task

        if task_list is None:
            task_list= []
        obj_list= []
        for src in src_list:
            obj_file= env.getObjPath( src )
            obj_list.append( obj_file )
            task= self.findTask( obj_file )
            if task == None:
                task= self.addObjTask( env, obj_file, [src] )
            task_list.append( task )

        command= env.getBuildCommand_Link( abs_target, obj_list )

        task= Depend.ExeTask( env, abs_target, obj_list, command, task_list )
        self.addTask( abs_target, task )
        return  task


    def addLibTask( self, env, name, src_list, task_list= None, target= None ):
        if target is None:
            target= env.getLibPath( name )
        abs_target= self.getGenericPath( target )
        task= self.findTask( abs_target )
        if task != None:
            return  task

        if task_list is None:
            task_list= []
        obj_list= []
        for src in src_list:
            obj_file= env.getObjPath( src )
            obj_list.append( obj_file )
            task= self.findTask( obj_file )
            if task == None:
                task= self.addObjTask( env, obj_file, [src] )
            task_list.append( task )

        command= env.getBuildCommand_Lib( abs_target, obj_list )

        task= Depend.ExeTask( env, abs_target, obj_list, command, task_list )
        self.addTask( abs_target, task )
        return  task


    def addDllTask( self, env, name, src_list, task_list= None, target= None ):
        if target is None:
            target= env.getDllPath( name )
        abs_target= self.getGenericPath( target )
        task= self.findTask( abs_target )
        if task != None:
            return  task

        if task_list is None:
            task_list= []
        obj_list= []
        for src in src_list:
            obj_file= env.getObjPath( src )
            obj_list.append( obj_file )
            task= self.findTask( obj_file )
            if task == None:
                task= self.addObjTask( env, obj_file, [src] )
            task_list.append( task )

        command= env.getBuildCommand_Dll( abs_target, obj_list )

        task= Depend.ExeTask( env, abs_target, obj_list, command, task_list )
        self.addTask( abs_target, task )
        return  task


    def addLipoTask( self, env, name, lib_list, task_list= None, target= None ):
        if target is None:
            target= env.getLibPath( name )
        abs_target= self.getGenericPath( target )
        task= self.findTask( abs_target )
        if task != None:
            return  task
        if task_list is None:
            task_list= []
        command= env.getBuildCommand_Lipo( abs_target, lib_list )
        task= Depend.ExeTask( env, abs_target, lib_list, command, task_list )
        self.addTask( abs_target, task )
        return  task


#    def addDllTask( self, env, target, src_list ):
#        dll_target= env.getDllPath( target )
#        abs_target= self.getGenericPath( dll_target )
#        task= self.findTask( abs_target )
#        if task != None:
#            return  task
#        lib_task= self.addLibTask( env, target, src_list )
#
#        command= env.getBuildCommand_Dll( dll_target, [lib_task.target] )
#        task= Depend.ExeTask( env, abs_target, [lib_task.target], command, [lib_task] )
#        self.addTask( abs_target, task )
#        return  task


#    def addSimpleExeTask( self, env, target, src_list ):
#        target= env.getExePath( target )
#        abs_target= self.getGenericPath( target )
#        task= self.findTask( abs_target )
#        if task != None:
#            return  task
#
#        command= env.getBuildCommand_Link( target, src_list )
#        task= Depend.ExeTask( env, abs_target, src_list, command, [] )
#        self.addTask( abs_target, task )
#        return  task


    def addGroupTask( self, env, task_name, task_list ):
        task= self.findTask( task_name )
        if task != None:
            raise BuildUtility.FLB_Error( 'task "%s" already exists' % task_name )
            return  task
        return  self.addTask( task_name, Depend.GroupTask( env, task_name, task_list ) )

    def addNamedTask( self, env, task_name, task_list ):
        return  self.addGroupTask( env, task_name, task_list )

    def addScriptTask( self, env, task_name, script, task_list= None ):
        task= self.findTask( task_name )
        if task != None:
            raise BuildUtility.FLB_Error( 'task "%s" already exists' % task_name )
            return  task
        if task_list is None:
            task_list= []
        return  self.addTask( task_name, Depend.ScriptTask( env, task_name, script, task_list ) )

    def addSubmoduleTasks( self, env, task_name, module_list, target_name= None, task_list= None ):
        if task_list is None:
            task_list= []
        if target_name is None:
            target_name= task_name
        for dir in module_list:
            task= self.findTask( dir + '/' + target_name )
            if task is not None:
                task_list.append( task )
        if task_list != []:
            return  self.addGroupTask( env, task_name, task_list )
        return  None


    def addCleanTask( self, env, task_name, task_list= None ):
        def command( task ):
            Log.p( 'Clean: '+ os.path.join( task.cwd, task.env.OUTPUT_OBJ_DIR ) )
            BuildUtility.RemoveTree( os.path.join( task.cwd, task.env.OUTPUT_OBJ_DIR ) )
        clean_task= self.addScriptTask( env, task_name, command, task_list )
        clean_task.cwd= os.getcwd()
        return  clean_task

    def addSequentialTask( self, env, task_name, task_list ):
        return  self.addTask( task_name, Depend.SequentialTask( env, task_name, task_list ) )

    #--------------------------------------------------------------------------

    def addLibTasks( self, env, task_name, lib_name, src_list, config_list, arch_list= None, inc_func= None, task_list= None ):
        if arch_list is None:
            arch_list= env.getSupportArchList()
        task_group= []
        for config in config_list:
            for arch in arch_list:
                local_env= env.clone()
                local_env.setConfig( config )
                local_env.setTargetArch( arch )
                if inc_func:
                    inc_func( local_env )
                local_env.refresh()
                task= self.addLibTask( local_env, lib_name, src_list, task_list )
                task_group.append( task )
        return  self.addGroupTask( env, task_name, task_group )

    def addLipoTasks( self, env, task_name, lib_name, src_list, config_list, arch_list= None, inc_func= None, task_list= None ):
        if arch_list is None:
            arch_list= env.getSupportArchList()
        task_group= []
        for config in config_list:
            task_arch= []
            name_arch= []
            for arch in arch_list:
                local_env= env.clone()
                local_env.setConfig( config )
                local_env.setTargetArch( arch )
                if inc_func:
                    inc_func( local_env )
                local_env.refresh()
                task= self.addLibTask( local_env, lib_name, src_list, task_list )
                task_arch.append( task )
                name_arch.append( task.target )
            if task_list:
                task_arch.extend( task_list )
            local_env= env.clone()
            local_env.setConfig( config )
            local_env.setTargetArch( 'universal' )
            local_env.refresh()
            task= self.addLipoTask( local_env, lib_name, name_arch, task_arch )
            task_group.append( task )
        return  self.addGroupTask( env, task_name, task_group )

    def addDllTasks( self, env, task_name, lib_name, src_list, config_list, arch_list, lib_func= None, task_list= None ):
        if arch_list is None:
            arch_list= env.getSupportArchList()
        task_group= []
        for config in config_list:
            for arch in arch_list:
                local_env= env.clone()
                local_env.setConfig( config )
                local_env.setTargetArch( arch )
                if lib_func:
                    lib_func( local_env )
                local_env.refresh()
                task= self.addDllTask( local_env, lib_name, src_list, task_list )
                task_group.append( task )
        return  self.addGroupTask( env, task_name, task_group )

    def addExeTasks( self, env, task_name, exe_name, src_list, config_list, arch_list= None, lib_func= None, exe_func= None, task_list= None ):
        if arch_list is None:
            arch_list= env.getSupportArchList()
        task_group= []
        for config in config_list:
            for arch in arch_list:
                local_env= env.clone()
                local_env.setConfig( config )
                local_env.setTargetArch( arch )
                if lib_func:
                    lib_func( local_env )
                if exe_func:
                    target= exe_func( local_env )
                else:
                    target= local_env.getExeName( exe_name + '_' + local_env.getTargetArch() + '_' + local_env.getConfig() )
                local_env.refresh()
                task= self.addExeTask( local_env, exe_name, src_list, task_list, target= target )
                task_group.append( task )
        return  self.addGroupTask( env, task_name, task_group )

    #--------------------------------------------------------------------------

    def createSourceFile( self, env, file_name ):
        return  Depend.SourceFile( env, file_name )

    #--------------------------------------------------------------------------
    def nameToTaskList( self, task_name_list ):
        task_list= []
        for task_name in task_name_list:
            task= self.findTask( task_name )
            if task == None:
                raise BuildUtility.FLB_Error( 'task "%s" not found' % task_name )
            task_list.append( task )
        return  task_list

    def runSequentialTask( self, task_list ):
        task_count= len(task_list)
        if task_count >= 2:
            for i in range(task_count-1):
                task_list[i].onCompleteTask( task_list[i+1] )
        if task_count >= 1:
            self.addJob( task_list[0] )

    #--------------------------------------------------------------------------

    def f_list( self ):
        self.task_cache.list()

    def f_platforms( self ):
        for platform in self.platform_table:
            env= self.createTargetEnvironment( platform )
            if env.isValid():
                Log.p( '[%s]--------' % platform )
                env.summary()



#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def load_config():
    script_bin_path= os.path.dirname( sys.argv[0] )
    config_path= os.path.join( script_bin_path, 'local_config.txt' )
    opt_dict= {}
    if os.path.exists( config_path ):
        with open( config_path, 'r' ) as fi:
            for line in fi:
                line= line.strip( ' \t\n' )
                if line == '' or line[0] == '#':
                    continue
                word= line.split()
                opt_dict[word[0]]= word[1]
    return  opt_dict


def usage():
    Log.p( 'FlatBuildTool v1.42 Hiroyuki Ogasawara' )
    Log.p( 'usage: python FlatBuildTool.py [<options>] [<target>...]' )
    Log.p( '  -f <BuildFile.py>  default : FLB_Makefile.py' )
    Log.p( '  --dump' )
    Log.p( '  --job <thread>     default : system thread count' )
    Log.p( '  --list             display all targets' )
    Log.p( '  --platforms' )
    Log.p( '  --opt <env_name>=<value>' )
    Log.p( '  -v, --verbose' )
    Log.p( '  --debug' )
    Log.p( 'parallel action: target1 target2 ...' )
    Log.p( 'sequential action: target1,target2,...' )
    sys.exit( 0 )


def main( argv ):
    makefile= 'FLB_Makefile.py'
    default_task= 'build'
    debug_flag= False
    dump_flag= False
    func_command= None
    env_dump= False
    job_count= 0
    action_list= []
    opt_dict= load_config()
    acount= len( argv )
    ai= 1
    while ai < acount:
        arg= argv[ai]
        if arg[0] == '-':
            if arg == '-f':
                ai+= 1
                if ai < acount:
                    makefile= argv[ai]
            elif arg == '--env':
                ai+= 1
                if ai < acount:
                    platform= argv[ai]
                env_dump= True
            elif arg == '--opt':
                ai+= 1
                if ai < acount:
                    opts= argv[ai].split( '=' )
                    opt_dict[opts[0]]= opts[1]
            elif arg == '--job':
                ai+= 1
                if ai < acount:
                    job_count= int( argv[ai] )
            elif arg == '--debug':
                debug_flag= True
                Log.DebugLevel= 2
            elif arg == '-v' or arg == '--verbose':
                debug_flag= True
                Log.DebugLevel= 1
            elif arg == '--dump':
                dump_flag= True
            elif arg == '--list':
                func_command= 'f_list'
            elif arg == '--platforms':
                func_command= 'f_platforms'
            else:
                usage()
        else:
            default_task= None
            action_list.append( arg )
        ai+= 1

    if default_task:
        action_list.append( default_task )
    if makefile != None:
        start_time_real= time.perf_counter()
        try:
            tool= BuildTool( job_count, opt_dict )
            tool.execScript( makefile )
            if func_command:
                getattr( tool, func_command )()
            else:
                for task_name in action_list:
                    actions= task_name.split(',')
                    tool.runSequentialTask( tool.nameToTaskList( actions ) )
            tool.wait()
            if dump_flag:
                tool.dump()
            if tool.result_code:
                return  tool.result_code
        except Exception as e:
            if not debug_flag:
                print( e )
            else:
                raise
        finally:
            Log.p( 'time %f' % ( time.perf_counter() - start_time_real ) )
    else:
        usage()

    Log.d( 'OK' )
    return  0


if __name__ == '__main__':
    sys.exit( main( sys.argv ) )

