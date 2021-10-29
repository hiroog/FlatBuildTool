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

        self.WASISDK_ROOT= tool.getEnv( 'WASISDK_ROOT' )
        if not self.WASISDK_ROOT:
            return

        self.setDefault()


    def summary( self ):
        super().summary()


    def isValid( self ):
        return  self.WASISDK_ROOT is not None


    def setDefault( self ):
        self.setTargetPlatform( 'WASI' )

        self.setConfig( 'Debug' )

        self.CMD_CC= os.path.join( self.WASISDK_ROOT, 'bin/clang' )
        self.CMD_LINK= self.CMD_CC
        self.CMD_LIB= os.path.join( self.WASISDK_ROOT, 'bin/ar' )

        self.addCCFlags( [
		'--target=wasm32-wasi',
		'-fno-exceptions',
		'--sysroot=' + os.path.join( self.WASISDK_ROOT, 'share/wasi-sysroot' ),
		'-DFLB_TARGET_WASI=1'
		] )

        self.refresh()

    #--------------------------------------------------------------------------

    def setupCCFlags( self ):
        self.CC_FLAGS_R= []
        table_config= {
            'Debug'   : '-O0 -g -D_DEBUG',
            'Release' : '-Os -g -O3 -DNDEBUG',
            'Retail'  : '-Os -O3 -DNDEBUG -DFLB_RETAIL=1',
            }
        self.CC_FLAGS_R.extend( table_config[ self.getConfig() ].split() )
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



