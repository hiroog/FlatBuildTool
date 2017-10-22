# FlatBuildTool 2017/09/15 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  PlatformCommon
from BuildUtility import Log


class TargetEnvironment( PlatformCommon.TargetEnvironmentCommon ):

    def __init__( self, tool, parent= None ):
        super().__init__( tool, parent )

        if not self.getHostPlatform() == 'macOS':
            return

        self.CMD_CC= '/usr/bin/clang++'
        self.CMD_LINK= '/usr/bin/clang++'
        self.CMD_LIB= 'ar'

        self.setDefault()


    def summary( self ):
        super().summary()

    def isValid( self ):
        return  self.getHostPlatform() == 'macOS'


    def setDefault( self ):
        self.setTargetPlatform( 'macOS' )

        self.setConfig( 'Debug' )
        self.addCCFlags( '-Wall -std=gnu++14 -fno-rtti -fno-exceptions -ffast-math'.split() )
        self.addCCFlags( '-fmessage-length=0 -pipe -Wno-trigraphs -Wreturn-type -gdwarf-2'.split() )

        self.addLibrary( [ 'stdc++', 'pthread', 'm'] )

        self.refresh()


    #--------------------------------------------------------------------------


    def setupCCFlags( self ):

        self.CC_FLAGS_R= []
        table_config= {
                'Debug'   : "-O0 -D_DEBUG",
                'Release' : "-Os -O3 -DNDEBUG",
                'Retail'  : "-Os -O3 -DNDEBUG -DFLB_RETAIL=1",
            }
        self.CC_FLAGS_R.extend( table_config[ self.getConfig() ].split() )
        self.CC_FLAGS_R.extend( self.CC_FLAGS )

        table_arch= {
            'x86':   '-m32 -msse3 -mssse3 -msse4.1 -maes',
            'x64':   '-m64 -msse3 -mssse3 -msse4.1 -maes',
            }
        self.CC_FLAGS_R.extend( table_arch[ self.getTargetArch() ].split() )

        for inc in self.INCLUDE_PATH_R:
            #print( 'INCLUDE=' + inc )
            self.CC_FLAGS_R.append( '-I' + inc )



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
        command.append( '-c' )
        command.extend( self.CC_FLAGS_R )
        for src in src_list:
            command.append( src )
        command.append( '-o' )
        command.append( target )
        return  command

    def getBuildCommand_Link( self, target, src_list ):
        command= []
        command.append( self.CMD_CC )
        command.append( '-o' )
        command.append( target )
        for src in src_list:
            command.append( src )
        command.extend( self.LINK_FLAGS_R )
        return  command

    def getBuildCommand_Lib( self, target, src_list ):
        command= []
        command.append( self.CMD_LIB )
        command.append( 'crs' )
        command.append( target )
        for src in src_list:
            command.append( src )
        command.extend( self.LIB_FLAGS_R )
        return  command









