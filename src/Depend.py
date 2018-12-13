# FlatBuildTool 2017/07/20 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  re
import  time
import  threading
import  BuildUtility
from BuildUtility import Log

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


class TimeStampCache:

    def __init__( self, tool ):
        self.tool= tool
        self.cache= {}

    def getTimeStamp( self, file_name ):
        l_name= self.tool.getGenericPath( file_name )
        if l_name in self.cache:
            return  self.cache[ l_name ]
        if os.path.exists( file_name ):
            file_time= os.path.getmtime( file_name )
            self.cache[ l_name ]= file_time
            return  file_time
        return  None

    def removeEntry( self, file_name ):
        l_name= self.tool.getGenericPath( file_name )
        if l_name in self.cache:
            del self.cache[ l_name ]

    def forceUpdate( self, file_name ):
        if os.path.exists( file_name ):
            file_time= os.path.getmtime( file_name )
            l_name= self.tool.getGenericPath( file_name )
            self.cache[ l_name ]= file_time

    def clear( self ):
        self.cache= {}

    def dump( self ):
        Log.p( '-------------------' )
        Log.p( 'TimeStamp cache:' )
        for l_name in self.cache:
            file_time= self.cache[ l_name ]
            ts= time.localtime( file_time ) 
            Log.p( '* %s %s' % ( time.strftime( '%Y/%m/%d %H:%M:%S', ts ), l_name) )
        Log.p( '-------------------' )



class SourceFileCache:

    def __init__( self, tool ):
        self.tool= tool
        self.cache= {}


    def getSourceFile( self, file_name ):
        l_name= self.tool.getGenericPath( file_name )
        if l_name in self.cache:
            return  self.cache[ l_name ]
        return  None


    def addSourceFile( self, file_name, env ):
        l_name= self.tool.getGenericPath( file_name )
        source_file= env.createSourceFile( l_name )
        self.cache[ l_name ]= source_file
        return  source_file


    def dump( self ):
        Log.p( '-------------------' )
        Log.p( 'SourceFile cache:' )
        for l_name in self.cache:
            file= self.cache[ l_name ]
            Log.p( '* %s' % l_name )
            for src in file.src_list:
                Log.p( '   include "%s"' % src )
        Log.p( '-------------------' )




class TaskCache:

    def __init__( self, tool ):
        self.tool= tool
        self.cache= {}
        self.prefix= []
        self.prefix_name= None


    def findTask( self, task_name ):
        #l_name= self.tool.getGenericPath( task_name )
        #l_name= task_name
        l_name= self.getPrefix( task_name )
        if l_name in self.cache:
            return  self.cache[l_name]
        return  None


    def addTask( self, task_name, task ):
        #l_name= self.tool.getGenericPath( task_name )
        #l_name= task_name
        l_name= self.getPrefix( task_name )
        self.cache[l_name]= task
        return  task


    def removeTask( self, task_name ):
        #l_name= self.tool.getGenericPath( task_name )
        l_name= task_name
        if l_name in self.cache:
            return  self.cache.pop( l_name )
        return  None

    def addPrefix( self, prefix ):
        self.prefix.append( prefix )
        self.buildPrefixCache()

    def popPrefix( self ):
        self.prefix.pop()
        self.buildPrefixCache()

    def buildPrefixCache( self ):
        base= None
        for pre in self.prefix:
            if base is not None:
                base+= pre + '/'
            else:
                base= pre + '/'
        if base is not None:
            self.prefix_name= base
        else:
            self.prefix_name= None

    def getPrefix( self, name ):
        if BuildUtility.IsRoot( name ):
            return  name
        if self.prefix_name is None:
            return  name
        return  self.prefix_name + name
        #base= None
        #for pre in self.prefix:
        #    if base is not None:
        #        base+= '/' + pre
        #    else:
        #        base= pre
        #if base is not None:
        #    return   base + '/' + name
        #return  name


    def dump( self ):
        Log.p( '-------------------' )
        Log.p( 'Task cache:' )
        for l_name in self.cache:
            task= self.cache[ l_name ]
            Log.p( 'TASK: ' + l_name )
            for src in task.src_list:
                Log.p( '   src "%s"' % src )
            if getattr( task, 'command', None ):
                Log.p( '   cmd %s' % task.command )
            for dep in task.task_list:
                Log.p( '   dep %s' % str(dep) )
            for comp in task.callback_task:
                Log.p( '   cb  %s' % str(comp) )
        Log.p( '-------------------' )


    def list( self ):
        for l_name in self.cache:
            task= self.cache[ l_name ]
            Log.p( 'Task: "%s"' % l_name )
            #Log.p( '      target: %s' % task.target )
            #if getattr( task, 'command', None ):
            #    Log.p( '   cmd %s' % task.command )
            for dep in task.task_list:
                Log.p( '      --> %s' % str(dep) )
            #for comp in task.callback_task:
            #    Log.p( '   cb  %s' % str(comp) )





#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


class FileBase:

    def __init__( self, env, target ):
        self.tool= env.tool
        self.env= env
        self.target= target
        self.src_list= []   # 依存file


    # need update?
    def isBuild( self, context, target_time ):
        for src_file in self.src_list:
            if not os.path.exists( src_file ):
                raise BuildUtility.FLB_Error( 'internal error: "%s" not found' % src_file )
            src_time= self.tool.timestamp_cache.getTimeStamp( src_file )
            if src_time > target_time:
                return  'depend "%s"' % src_file
        for src_file in self.src_list:
            if src_file in context:
                continue
            context[src_file]= True
            file= self.tool.source_cache.getSourceFile( src_file )
            if file == None:
                file= self.tool.source_cache.addSourceFile( src_file, self.env )
            result= file.isBuild( context, target_time )
            if result != None:
                return  result
        return  None





class ExeCompleteJob:

    def __init__( self, task, owner_task ):
        self.task= task
        self.owner_task= owner_task

    def run( self ):
        result= self.task.run()
        result= self.owner_task.completeFunc( result, self.task )
        return  result

#
#       depend.run -- callback task.signal ret result
#          ^                     |          ^
#          |                     v          |
# task.run + ret 0               +----------+
#
#



class TaskBase( FileBase ):

    def __init__( self, env, target ):
        super().__init__( env, target )
        self.task_list= []  # 依存task
        self.completed= False
        #self.error= False
        self.lock= threading.Lock()
        self.task_count= 0
        self.callback_task= []
        self.state_wait= False

    def __repr__( self ):
        return  self.target

    def isCompleted( self ):
        return  self.completed

    def setCompleted( self, flag ):
        self.completed= flag

    def addDependTasks( self, task_list ):
        self.task_list.extend( task_list )

    def addCompleteTask( self, task ):
        self.callback_task.append( task )

    def completeTask( self, result_code ):
        self.setCompleted( True )
        if result_code != 0:
            return  result_code
        for task in self.callback_task:
            Log.d( ' completeTask callback = ' + task.target )
            result_code= task.run()
            if result_code != 0:
                return  result_code
        return  0

    def inc( self ):
        with self.lock:
            self.task_count+= 1
            return  self.task_count

    def dec( self ):
        with self.lock:
            self.task_count-= 1
            return  self.task_count

    def signal( self ):
        count= self.dec()
        Log.d( ('signal %d ' + self.target) % count )
        if count == 0:
            Log.d( 'signal zero run preBuild ' + self.target )
            self.state_wait= False
            return  self.preBuild()
        return  0


    def build( self ):
        return  self.completeTask( 0 )

    def dependTask( self ):
        if len(self.task_list) != 0:
            for task in self.task_list:
                if not task.isCompleted():
                    self.inc()
            if self.task_count != 0:
                self.state_wait= True
                for task in self.task_list:
                    if not task.isCompleted():
                        Log.d( ' depend -> ' + task.target )
                        task.addCompleteTask( self )
                        self.tool.thread_pool.addJob( task )
                return  0
        return  self.preBuild()


    def run( self ):
        Log.d( 'RunTask: ' + self.target )
        if self.state_wait:
            return  self.signal()
        return  self.dependTask()


    def preBuild( self ):
        Log.d( 'Task prebuild= ' + self.target )
        if not os.path.exists( self.target ):
            return  self.build( 'new "%s"' % self.target )

        dest_time= self.tool.timestamp_cache.getTimeStamp( self.target )
        #print( 'TargetTime =' + str(dest_time) )
        result= self.isBuild( {}, dest_time )
        if result != None:
            return  self.build( result )
        return  self.completeTask( 0 )



#------------------------------------------------------------------------------
#------------------------------------------------------------------------------



class SourceFileC( FileBase ):

    pat_include= re.compile( r'^\s*#\s*include\s+"(.*)"' )
    pat_include_sys= re.compile( r'^\s*#\s*include\s+\<(.*)\>' )

    def __init__( self, env, target ):
        super().__init__( env, target )
        self.parsed= False
        self.parseInclude()



    def parseInclude( self ):
        if self.parsed:
            return
        self.src_list= []
        with open( self.target, 'r', encoding= 'UTF=8' ) as fi:
            for line in fi:
                pat= self.pat_include.search( line )
                if pat == None:
                    pat= self.pat_include_sys.search( line )
                if pat != None:
                    include_file= pat.group( 1 )
                    # expand include path
                    #print( 'parse inc=' + include_file )
                    include_file= self.env.searchIncludePath( self.target, include_file )
                    if include_file != None:
                        self.src_list.append( include_file )
                    else:
                        # ignore
                        pass
        self.parsed= True





#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


class ObjTask( TaskBase ):

    def __init__( self, env, target, src_list, command ):
        super().__init__( env, target )
        self.src_list= src_list
        self.command= command

    def build( self, message ):
        Log.p( 'ObjTask: ' + self.target )
        Log.p( '  <== ' + message )
        self.env.makeOutputDirectory( self.target )
        result_code= BuildUtility.ExecCommand( self.command )
        self.tool.timestamp_cache.removeEntry( self.target )
        if result_code == 0:
            Log.p( ' Ok ' + self.target )
        return  self.completeTask( result_code )


    def isBuild( self, context, target_time ):
        if not os.path.exists( self.target ):
            return  'new "%s"' % self.target
        for src in self.src_list:
            if not os.path.exists( src ):
                raise BuildUtility.FLB_Error( 'source file "%s" not found' % src )
        return  super().isBuild( context, target_time )


#    def run( self ):
#        if not os.path.exists( self.target ):
#            return  self.build( 'new "%s"' % self.target )
#
#        dest_time= self.tool.timestamp_cache.getTimeStamp( self.target )
#        result= self.isBuild( {}, dest_time )
#        if result != None:
#            return  self.build( result )
#        #self.setCompleted( True )
#        return  self.completeTask( 0 )


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


def commandSplitter( command ):
    if ';;' in command:
        cmd_list= []
        cur_args= []
        for param in command:
            if param == ';;':
                cmd_list.append( cur_args )
                cur_args= []
            else:
                cur_args.append( param )
        cmd_list.append( cur_args )
        return  cmd_list
    return  [command]


class ExeTask( TaskBase ):

    def __init__( self, env, target, src_list, command, task_list ):
        super().__init__( env, target )
        self.src_list= src_list
        self.command= command
        self.task_list= task_list


    def build( self, message ):
        Log.p( 'ExeTask: ' + self.target )
        Log.p( '  <== ' + message )
        self.env.makeOutputDirectory( self.target )
        #self.tool.thread_pool.addJob( CompileJob( self.tool, self.env, self.command ) )

        command_list= commandSplitter( self.command )
        #print( command_list )
        for command in command_list:
            if not isinstance( command[0], str ):
                command[0]( *command[1:] )
            else:
                result_code= BuildUtility.ExecCommand( command )
                if result_code != 0:
                    return  self.completeTask( result_code )

        self.tool.timestamp_cache.removeEntry( self.target )
        if result_code == 0:
            Log.p( '  Ok ' + self.target )
        return  self.completeTask( result_code )


    def isBuild( self, context, target_time ):
        #print( 'Exe isBuild ' + str(target_time) )
        for src_file in self.src_list:
            if not os.path.exists( src_file ):
                raise BuildUtility.FLB_Error( 'internal error: "%s" not found' % src_file )
            src_time= self.tool.timestamp_cache.getTimeStamp( src_file )
            #print( src_file + ' :  ' + str(src_time) + ' ==  ' + str(target_time) )
            if src_time > target_time:
                return  'depend "%s"' % src_file
        return  None





class ExeTaskFromSrc( TaskBase ):


    def __init__( self, env, target, src_list, command ):
        super().__init__( env, target )
        self.src_list= []
        self.command= command
        self.source_list= src_list


    def build( self, message ):
        Log.p( 'ExeTask: ' + self.target )
        Log.p( '  <== ' + message )
        result_code= BuildUtility.ExecCommand( self.command )
        if result_code == 0:
            Log.p( '  Ok ' + self.target )
        return  result_code


    def isBuild( self, context, target_time ):
        for src_file in self.src_list:
            if not os.path.exists( src_file ):
                raise BuildUtility.FLB_Error( 'internal error: "%s" not found' % src_file )
            src_time= self.tool.timestamp_cache.getTimeStamp( src_file )
            if src_time > target_time:
                return  'depend "%s"' % src_file
        return  None


    def run( self ):
        task_list= []
        obj_list= []
        for src in self.source_list:
            abs_src_file= os.path.abspath( src )
            obj_file= env.getObjPath( src )
            obj_list.append( obj_file )
            task= self.tool.findTask( obj_file )
            if task == None:
                task= self.env.addObjTask( obj_file, abs_src_file )
            task_list.append( task )
        self.command= self.env.getBuildCommand_Link( self.target, obj_list )
        self.task_list= task_list
        self.src_list= obj_list

        return  super().__run__()


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


# unuse
class LibTask( TaskBase ):

    def __init__( self, env, target, src_list, command, task_list ):
        super().__init__( env, target )
        self.src_list= src_list
        self.command= command
        self.task_list= task_list


    def build( self, message ):
        Log.p( 'LibTask: ' + self.target )
        Log.p( '  <== ' + message )
        result_code= BuildUtility.ExecCommand( self.command )
        self.tool.timestamp_cache.removeEntry( self.target )
        if result_code == 0:
            Log.p( '  Ok ' + self.target )
        return  result_code


    def isBuild( self, context, target_time ):
        #print( 'Exe isBuild ' + str(target_time) )
        for src_file in self.src_list:
            if not os.path.exists( src_file ):
                raise BuildUtility.FLB_Error( 'internal error: "%s" not found' % src_file )
            src_time= self.tool.timestamp_cache.getTimeStamp( src_file )
            #print( src_file + ' :  ' + str(src_time) + ' ==  ' + str(target_time) )
            if src_time > target_time:
                return  'depend "%s"' % src_file
        return  None



#------------------------------------------------------------------------------
#------------------------------------------------------------------------------


class NamedTask( TaskBase ):

    def __init__( self, env, target, task_list ):
        super().__init__( env, target )
        self.task_list= task_list

    def preBuild( self ):
        Log.d( 'Named task "%s" completed' % self.target )
        return  self.completeTask( 0 )



class ScriptTask( TaskBase ):

    def __init__( self, env, target, script, src_list, task_list ):
        super().__init__( env, target )
        self.src_list= src_list
        self.task_list= task_list
        self.script= script
        self.args= None

    def preBuild( self ):
        if self.args is None:
            self.script( self )
        else:
            self.script( *self.args )
        Log.d( 'Script task "%s" completed' % self.target )
        return  self.completeTask( 0 )



class SequentialTask( TaskBase ):

    def __init__( self, env, target, task_list ):
        super().__init__( env, target )
        self.task_list= [ task_list.pop(0) ]
        self.sequential_list= task_list

    def signal( self, result_code, task ):
        if result_code != 0:
            return  result_code
        if len( self.sequential_list ) == 0:
            Log.d( 'Sequential task "%s" completed' % self.target )
            return  self.completeTask( 0 )
        task= self.sequential_list.pop(0)
        if not task.isCompleted():
            task.addCompleteTask( self )
            self.tool.addJob( task )
            return  0
        return  self.completeTask( 0 )

    def preBuild( self ):
        Log.d( 'Sequential task "%s" completed' % self.target )
        return  self.completeTask( 0 )




#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

