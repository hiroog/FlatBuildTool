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

        #script_bin_path= os.path.dirname(__file__)
        script_bin_path= os.path.dirname(sys.argv[0])

        sys.path.append( script_bin_path )
        StartupScript= os.path.join( script_bin_path, 'FLB_Default.py' )

        if os.path.exists( StartupScript ):
            self.execScript( StartupScript )

    def dump( self ):
        self.timestamp_cache.dump()
        self.source_cache.dump()
        self.task_cache.dump()


    #--------------------------------------------------------------------------

    def addPlatform( self, platform_name, platform_env ):
        Log.d( 'Load platform : ' + platform_name )
        self.platform_table[ platform_name ]= platform_env

    def createTargetEnvironment( self, platform= None ):
        if platform == None:
            platform= self.global_env.getHostPlatform()
        if platform in self.platform_table:
            return  self.platform_table[ platform ].TargetEnvironment( self, self.global_env )
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
        self.thread_pool.join()

    def getEnv( self, name, default_value= None ):
        #return  BuildUtility.GetEnv( name, default_value )
        if name in os.environ:
            return  os.environ[name]
        return  default_value

    def findPath( self, path, env= None ):
        return  BuildUtility.FindPath( path, env )

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
        #abs_target= os.path.abspath( target )
        abs_target= self.getGenericPath( target )
        task= self.findTask( abs_target )
        if task != None:
            return  task

        abs_src_list= []
        task_list= []
        for src in src_list:
            #abs_src= os.path.abspath( src )
            abs_src= self.getGenericPath( src )
            abs_src_list.append( abs_src )
            task= self.findTask( abs_src )
            if task != None:
                task_list.append( task )

        command= env.getBuildCommand_CC( target, abs_src_list )
        task= Depend.ObjTask( env, abs_target, abs_src_list, command )
        task.addDependTasks( task_list )
        self.addTask( abs_target, task )
        return  task


    def addExeTask( self, env, target, src_list ):
        target= env.getExePath( target )
        abs_target= self.getGenericPath( target )
        task= self.findTask( abs_target )
        if task != None:
            return  task

        task_list= []
        obj_list= []
        for src in src_list:
            obj_file= env.getObjPath( src )
            obj_list.append( obj_file )
            task= self.findTask( obj_file )
            if task == None:
                task= self.addObjTask( env, obj_file, [src] )
            task_list.append( task )

        command= env.getBuildCommand_Link( target, obj_list )

        task= Depend.ExeTask( env, abs_target, obj_list, command, task_list )
        self.addTask( abs_target, task )
        return  task


    def addLibTask( self, env, target, src_list ):
        target= env.getLibPath( target )
        abs_target= self.getGenericPath( target )
        task= self.findTask( abs_target )
        if task != None:
            return  task

        task_list= []
        obj_list= []
        for src in src_list:
            obj_file= env.getObjPath( src )
            obj_list.append( obj_file )
            task= self.findTask( obj_file )
            if task == None:
                task= self.addObjTask( env, obj_file, [src] )
            task_list.append( task )

        command= env.getBuildCommand_Lib( target, obj_list )

        task= Depend.ExeTask( env, abs_target, obj_list, command, task_list )
        self.addTask( abs_target, task )
        return  task



    def addDllTask( self, env, target, src_list ):
        target= env.getDllPath( target )
        abs_target= self.getGenericPath( target )
        task= self.findTask( abs_target )
        if task != None:
            return  task

        task_list= []
        obj_list= []
        for src in src_list:
            obj_file= env.getObjPath( src )
            obj_list.append( obj_file )
            task= self.findTask( obj_file )
            if task == None:
                task= self.addObjTask( env, obj_file, [src] )
            task_list.append( task )

        command= env.getBuildCommand_Dll( target, obj_list )

        task= Depend.ExeTask( env, abs_target, obj_list, command, task_list )
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



    def addSimpleExeTask( self, env, target, src_list ):
        target= env.getExePath( target )
        abs_target= self.getGenericPath( target )
        task= self.findTask( abs_target )
        if task != None:
            return  task

        command= env.getBuildCommand_Link( target, src_list )
        task= Depend.ExeTask( env, abs_target, src_list, command, [] )
        self.addTask( abs_target, task )
        return  task


    def addNamedTask( self, env, target, task_list, *mode ):
        task= self.findTask( target )
        if task != None:
            raise BuildUtility.FLB_Error( 'task "%s" already exists' % target )
            return  task
        return  self.addTask( target, Depend.NamedTask( env, target, task_list ) )


    def addScriptTask( self, env, target, script, src_list= [], task_list= [] ):
        task= self.findTask( target )
        if task != None:
            raise BuildUtility.FLB_Error( 'task "%s" already exists' % target )
            return  task
        return  self.addTask( target, Depend.ScriptTask( env, target, script, src_list, task_list ) )

    def addSubmoduleTasks( self, env, name, module_list, target_name= None ):
        task_list= []
        if target_name is None:
            target_name= name
        for dir in module_list:
            task= self.findTask( dir + '/' + target_name )
            if task is not None:
                task_list.append( task )
        if task_list != []:
            return  self.addNamedTask( env, name, task_list )
        return  None



    #--------------------------------------------------------------------------





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
        prev_task= None
        first_task= None
        for task in task_list:
            if first_task == None:
                first_task= task
            if prev_task:
                prev_task.addCompleteTask( task )
            prev_task= task
        if first_task:
            self.addJob( first_task )



    #--------------------------------------------------------------------------


    def list( self ):
        self.task_cache.list()






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
    print( opt_dict )
    return  opt_dict


def usage():
    Log.p( 'FlatBuildTool v1.18 Hiroyuki Ogasawara' )
    Log.p( 'usage: python FlatBuildTool.py [<options>] [<target>...]' )
    Log.p( '  -f <BuildFile.py>  default : FLB_Makefile.py' )
    Log.p( '  --debug' )
    Log.p( '  --dump' )
    Log.p( '  --job <thread>     default : system thread count' )
    Log.p( '  --list             display all targets' )
#    Log.p( '  --env <platform>' )
    Log.p( '  --opt <prop_name>=<value>' )
    Log.p( 'parallel action: target1 target2 ...' )
    Log.p( 'sequential action: target1,target2,...' )
    sys.exit( 0 )


def main():
    makefile= 'FLB_Makefile.py'
#    platform= None
    default_task= 'build'
    debug_flag= False
    dump_flag= False
    list_flag= False
    env_dump= False
    job_count= 0
    action_list= []
    opt_dict= load_config()
    acount= len( sys.argv )
    ai= 1
    while ai < acount:
        arg= sys.argv[ai]
        if arg[0] == '-':
            if arg == '-f':
                ai+= 1
                if ai < acount:
                    makefile= sys.argv[ai]
            elif arg == '--env':
                ai+= 1
                if ai < acount:
                    platform= sys.argv[ai]
                env_dump= True
            elif arg == '--opt':
                ai+= 1
                if ai < acount:
                    opts= sys.argv[ai].split( '=' )
                    opt_dict[opts[0]]= opts[1]
            elif arg == '--job':
                ai+= 1
                if ai < acount:
                    job_count= int( sys.argv[ai] )
            elif arg == '--debug':
                debug_flag= True
                Log.DebugLevel= 1
            elif arg == '--dump':
                dump_flag= True
            elif arg == '--list':
                list_flag= True
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
            if list_flag:
                tool.list()
            else:
                for task_name in action_list:
                    actions= task_name.split(',')
                    tool.runSequentialTask( tool.nameToTaskList( actions ) )
            tool.wait()
            if dump_flag:
                tool.dump()
        except Exception as e:
            if not debug_flag:
                print( e )
            else:
                raise
        finally:
            pass
        Log.p( 'time %f' % ( time.perf_counter() - start_time_real ) )
    else:
        usage()

    Log.d( 'OK' )


if __name__ == '__main__':
    main()

