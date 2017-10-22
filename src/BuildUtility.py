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
    def d( message ):
        if Log.DebugLevel >= 1:
            print( message )

    @staticmethod
    def e( message ):
        print( 'ERROR: ' + message )

    @staticmethod
    def p( message ):
        print( message )



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
        shutil.rmtree( path )



def GetEnv( name, default_value= None ):
    if name in os.environ:
        return  os.environ[name]
    return  default_value


def GetFullPath( path ):
    return  os.path.abspath( path )


def FindPath( path, env ):
    result= os.path.abspath( path )
    if os.path.exists( result ):
        return  result
    result= GetEnv( env )
    if result is not None:
        return  result
    return  None



def GetTimeStamp( file_name ):
    if os.path.exists( file_name ):
        return  os.path.getmtime( file_name )
    return  0


def CopyFilesDir( src_list, dest_dir ):
    if not os.path.exists( dest_dir ):
        os.mkdirs( dest_dir )
    for src in src_list:
        dir,name= os.path.split( src )
        dest_file= os.path.join( dest_dir, name )
        src_time= GetTimeStamp( src )
        dest_time= GetTimeStamp( dest_file )
        if src_time > dest_time:
            Log.p( 'copy ' + src + ' ' + dest_file )
            shutil.copyfile( src, dest_file )



def CopyFiles( src_list, dest_list ):
    for src,dest in zip( src_list, dest_list ):
        dir,name= os.path.split( dest )
        if not os.path.exists( dir ):
            os.mkdirs( dir )
        src_time= GetTimeStamp( src )
        dest_time= GetTimeStamp( dest )
        if src_time > dest_time:
            Log.p( 'copy ' + src + ' ' + dest )
            shutil.copyfile( src, dest )




