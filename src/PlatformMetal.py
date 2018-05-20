# FlatBuildTool 2017/11/17 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  PlatformCommon
import  BuildUtility
from BuildUtility import Log


class TargetEnvironment( PlatformCommon.TargetEnvironmentCommon ):

    def __init__( self, tool, parent= None ):
        super().__init__( tool, parent )

        self.SDK_ROOT= None
        if not self.getHostPlatform() == 'macOS':
            return

        self.SDK_ROOT= '/Applications/Xcode.app/Contents/Developer/Platforms'
        self.CMD_CC= 'metal'
        self.CMD_LINK= 'metal-link'
        self.CMD_LIB= 'metal-ar'

        self.setDefault()


    def summary( self ):
        super().summary()

    def isValid( self ):
        return  (self.SDK_ROOT is not None) and os.path.exists( self.SDK_ROOT )


    def setDefault( self ):
        self.setTargetPlatform( 'Metal' )

        self.setConfig( 'Debug' )
        self.addCCFlags( '-x metal -Wall -emit-llvm -gline-tables-only -ffast-math'.split() )

        self.refresh()


    #--------------------------------------------------------------------------


    def setupCCFlags( self ):

        self.CC_FLAGS_R= []
        table_config= {
                'Debug'   : "-Os -O3 -D_DEBUG",
                'Release' : "-Os -O3 -DNDEBUG",
                'Retail'  : "-Os -O3 -DNDEBUG -DFLB_RETAIL=1",
            }
        self.CC_FLAGS_R.extend( table_config[ self.getConfig() ].split() )
        self.CC_FLAGS_R.extend( self.CC_FLAGS )

        table_arch= {
                'macos' :   '-std=osx-metal2.0 -arch air64',
                'ios'   :   '-std=ios-metal2.0 -arch air64',
            }

        self.CC_FLAGS_R.extend( table_arch[ self.getTargetArch() ].split() )

        talbe_cmd= {
                'macos' :   'MacOSX.platform',
                'ios'   :   'iPhoneOS.platform',
            }

        self.CMD_CC= os.path.join( self.SDK_ROOT, talbe_cmd[env.getTargetArch()], 'usr/bin/metal' )
        self.CMD_LIB= os.path.join( self.SDK_ROOT, talbe_cmd[env.getTargetArch()], 'usr/bin/metal-ar' )
        self.CMD_LIB2= os.path.join( self.SDK_ROOT, talbe_cmd[env.getTargetArch()], 'usr/bin/metallib' )

        for inc in self.INCLUDE_PATH_R:
            #print( 'INCLUDE=' + inc )
            self.CC_FLAGS_R.append( '-I' + inc )



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


    def getObjName( self, obj_name ):
        return  obj_name + '.air'

    def getLibName( self, obj_name ):
        return  obj_name + '.metal-ar'

    def getExeName( self, obj_name ):
        return  obj_name + '.metallib'

    def getSupportArchList( self ):
        return  [ 'macos', 'ios' ]




