# FlatBuildTool 2017/07/22 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  subprocess
import  shutil

#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class Log:
    DebugLevel= 0

    @staticmethod
    def d( *message ):
        if Log.DebugLevel >= 2:
            print( *message )

    @staticmethod
    def e( *message ):
        print( 'ERROR:', *message )

    @staticmethod
    def p( *message ):
        print( *message )

    @staticmethod
    def v( *message ):
        if Log.DebugLevel >= 1:
            print( *message )



class FLB_Error( Exception ):

    def __init__( self, message ):
        self.message= 'ERROR: ' + message

    def __str__( self ):
        return  self.message



def ExecCommand( command ):
    Log.d( 'ExecCommand ' + str(command) )
    log= ''
    code= 0
    try:
        proc= subprocess.Popen( command )
        proc.wait()
    except OSError:
        Log.e( 'Exception ExecCommand=' + str( command ) )
        raise
    code= proc.returncode
    Log.d( 'ExitCode=%d' % code )
    return  code



def IsRoot( path ):
    if path[0] == '/' or path[0] == '\\':
        return  True
    if len( path ) >= 3 and path[1] == ':':
        return  True
    return  False



def RemoveTree( path ):
    if os.path.exists( path ):
        Log.d( 'Remove Tree = ' + path )
        shutil.rmtree( path )



def RemoveFile( path ):
    if os.path.exists( path ):
        Log.d( 'Remove File = ' + path )
        os.remove( path )



def GetEnv( name, default_value= None ):
    if name in os.environ:
        return  os.environ[name]
    return  default_value



def GetFullPath( path ):
    return  os.path.abspath( path )



def FindPath( path, env= None ):
    result= os.path.abspath( path )
    if os.path.exists( result ):
        return  result
    if env is not None:
        result= GetEnv( env )
        if result is not None:
            if not os.path.exists( result ):
                Log.e( 'Not found', result )
            return  result
    Log.e( 'Path not found', path, env )
    return  None


def FindPaths( path_list ):
    for path in path_list:
        if path[0] == '$':
            path= GetEnv( path[1:] )
        result= os.path.abspath( path )
        if os.path.exists( result ):
            return  result
    Log.e( 'Path not found ' + str(path_list) )
    return  None


def GetTimeStamp( file_name ):
    if os.path.exists( file_name ):
        return  os.path.getmtime( file_name )
    return  0



def CopyFilesDir( src_list, dest_dir ):
    if not os.path.exists( dest_dir ):
        os.makedirs( dest_dir )
    for src in src_list:
        dir,name= os.path.split( src )
        dest_file= os.path.join( dest_dir, name )
        src_time= GetTimeStamp( src )
        dest_time= GetTimeStamp( dest_file )
        if src_time > dest_time:
            Log.p( 'copy ' + src + ' ' + dest_file )
            shutil.copyfile( src, dest_file )
            shutil.copymode( src, dest_file )



def CopyFilesPair( src_list ):
    for src,dest in src_list:
        dir,name= os.path.split( dest )
        if not os.path.exists( dir ):
            os.makedirs( dir )
        src_time= GetTimeStamp( src )
        dest_time= GetTimeStamp( dest )
        if src_time > dest_time:
            Log.p( 'copy ' + src + ' ' + dest )
            shutil.copyfile( src, dest )
            shutil.copymode( src, dest )



def CopyFiles( src_list, dest_list ):
    CopyFilesPair( zip( src_list, dest_list ) )





