# FlatBuildTool 2021/10/29 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  re
import  PlatformCommon
import  BuildUtility
from BuildUtility import Log



class TargetEnvironment( PlatformCommon.TargetEnvironmentCommon ):

    def __init__( self, tool, parent= None ):
        super().__init__( tool, parent )

        self.EMSDK_ROOT= tool.getEnv( 'EMSDK' )
        if not self.EMSDK_ROOT:
            return

        self.setDefault()


    def summary( self ):
        super().summary()


    def isValid( self ):
        return  self.EMSDK_ROOT is not None


    def setDefault( self ):
        self.setTargetPlatform( 'EMS' )

        self.setConfig( 'Debug' )

        self.CMD_CC= os.path.join( self.EMSDK_ROOT, 'upstream/emscripten/emcc' )
        self.CMD_LINK= self.CMD_CC
        self.CMD_LIB= os.path.join( self.EMSDK_ROOT, 'upstream/emscripten/emar' )

        #self.addCCFlags( '-sWASM=1'.split() )
        self.addCCFlags( ['-DFLB_TARGET_EMS=1'] )

        self.refresh()


    #--------------------------------------------------------------------------


    def setupCCFlags( self ):
        self.CC_FLAGS_R= []
        for inc in self.INCLUDE_PATH_R:
            self.CC_FLAGS_R.append( '-I' + inc )
        self.CC_FLAGS_R.extend( self.CC_FLAGS )


    #--------------------------------------------------------------------------

    def getBuildCommand_CC( self, target, src_list ):
        command= []
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
        command.append( BuildUtility.RemoveFile )
        command.append( target )
        command.append( ';;' )
        command.append( self.CMD_LIB )
        command.append( 'crs' )
        command.append( target )
        for src in src_list:
            command.append( src )
        command.extend( self.LIB_FLAGS_R )
        return  command

    #--------------------------------------------------------------------------

    def getSupportArchList( self ):
        return  [ 'wasm32' ]



