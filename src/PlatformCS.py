# FlatBuildTool 2017/09/16 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  platform
import  PlatformCommon
import  BuildUtility
from BuildUtility import Log

if platform.system() == 'Windows':
    import  winreg


class TargetEnvironment( PlatformCommon.TargetEnvironmentCommon ):

    def __init__( self, tool, parent= None ):
        super().__init__( tool, parent )

        self.CMD_CC= None
        self.CMD_LINK= None
        self.CMD_LIB= None

        self.SAVE_PATH= os.environ[ 'PATH' ]

        self.setDefault()


    def summary( self ):
        super().summary()

    def isValid( self ):
        return  self.CMD_CC is not None

    def setDefault( self ):

        if self.getHostArch() == 'x64':
            self.X86_PROGRAMFILES= os.environ['ProgramFiles(x86)']
        else:
            self.X86_PROGRAMFILES= os.environ['ProgramFiles']


        cs_search_path= [
                os.path.join( self.X86_PROGRAMFILES, 'Microsoft Visual Studio/2017/Professional/MSBuild/15.0/Bin/Roslyn' ),
                os.path.join( self.X86_PROGRAMFILES, 'Microsoft Visual Studio/2017/Community/MSBuild/15.0/Bin/Roslyn' ),
                os.path.join( self.X86_PROGRAMFILES, 'MSBuild/14.0/Bin' ),
                os.path.join( self.X86_PROGRAMFILES, 'MSBuild/12.0/Bin' ),
                'C:/Windows/Microsoft.NET/Framework64/v4.0.30319',
                'C:/Windows/Microsoft.NET/Framework64/v3.5',
                'C:/Windows/Microsoft.NET/Framework64/v3.0',
                'C:/Windows/Microsoft.NET/Framework/v4.0.30319',
                'C:/Windows/Microsoft.NET/Framework/v3.5',
                'C:/Windows/Microsoft.NET/Framework/v3.0',
            ]

        csc_path= self.findPath( cs_search_path )
        if csc_path is None:
            return

        Log.d( 'Found csc.exe [%s]' % cs_search_path )

        self.CMD_CC= os.path.join( csc_path, 'csc.exe' )
        self.refresh()



    #--------------------------------------------------------------------------


    def setupBinPath( self ):

        self.BIN_PATH_R= []
        self.BIN_PATH_R.extend( self.BIN_PATH )

        path_r= ''
        for path in self.BIN_PATH_R:
            path_r+= path + ';'
        os.environ[ 'PATH' ]= path_r + self.SAVE_PATH
        #print( 'PATH=' + str(os.environ['PATH']) )


    def setupIncludePath( self ):
        self.INCLUDE_PATH_R= []
        self.INCLUDE_PATH_R.extend( self.INCLUDE_PATH )


    def setupLibPath( self ):
        self.LIB_PATH_R= []
        self.LIB_PATH_R.extend( self.LIB_PATH )


    def setupCCFlags( self ):

        self.CC_FLAGS_R= []
        table_config= {
                'Debug'   : "/debug+",
                'Release' : "/optimize+ /debug+",
                'Retail'  : "/optimize+",
            }
        self.CC_FLAGS_R.extend( table_config[ self.getConfig() ].split() )
        self.CC_FLAGS_R.extend( self.CC_FLAGS )

        table_arch= {
                'x64'  : '-target:x64',
                'x86'  : '-target:x86',
                'arm7' : '-target:arm',
                'any'  : '-target:anycpu',
            }
        self.CC_FLAGS_R.extend( table_arch[ self.getTargetArch() ].split() )

        #for inc in self.INCLUDE_PATH_R:
        #    #print( 'INCLUDE=' + inc )
        #    self.CC_FLAGS_R.append( '-I' + inc )


    def setupLinkFlags( self ):

        self.LINK_FLAGS_R= []
        #for lib in self.LIB_PATH_R:
        #    #print( 'LIB=' + lib )
        #    self.LINK_FLAGS_R.append( '-LIBPATH:' + lib )
        #self.LINK_FLAGS_R.extend( self.LINK_FLAGS )
        #for lib in self.LINK_LIBS_R:
        #    self.LINK_FLAGS_R.append( self.getLibName( lib ) )




    #--------------------------------------------------------------------------

    def getBuildCommand_CC( self, target, src_list ):
        command= []
        if self.getOption( 'BRCC' ):
            config= self.getOption( 'BRCC_Config' )
            if config.python:
                command.append( config.python )
                command.append( os.path.join( config.BRCC_ROOT, 'src/brcc.py' ) )
            else:
                command.append( os.path.join( config.BRCC_ROOT, 'bin/brcc' ) )
            command.append( '---exe:' + self.CMD_CC )
        else:
            command.append( self.CMD_CC )
        #command.append( '-c' )
        command.extend( self.CC_FLAGS_R )
        for src in src_list:
            #abs_src= self.tool.host.getGenericPath( src )
            #command.append( abs_src )
            command.append( src )
        command.append( '/out:' + target )
        return  command

    def getBuildCommand_Link( self, target, src_list ):
        command= []
        command.append( self.CMD_CC )
        command.append( '-out:' + target )
        for src in src_list:
            command.append( src )
        command.append( '-target:exe' )
        command.extend( self.LINK_FLAGS_R )
        return  command

    def getBuildCommand_Lib( self, target, src_list ):
        command= []
        command.append( self.CMD_LIB )
        command.append( '-out:' + target )
        for src in src_list:
            command.append( src )
        command.append( '-target:library' )
        command.extend( self.LIB_FLAGS_R )
        return  command



    def getExeName( self, exe_name ):
        return  exe_name + '.exe'

    def getLibName( self, lib_name ):
        return  lib_name + '.lib'

    def getObjName( self, obj_name ):
        return  obj_name + '.obj'

    #--------------------------------------------------------------------------

    def getSupportArchList( self ):
        #return  [ 'any', 'x64', 'x86', 'any32', 'arm7' ]
        return  [ 'any' ]





