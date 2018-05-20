# FlatBuildTool 2017/11/01 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  PlatformCommon
import  BuildUtility
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
        self.setTargetPlatform( 'iOS' )
        self.setTargetArch( 'arm64' )
        self.SDK_PATH= '/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS11.1.sdk'

        self.setConfig( 'Debug' )
        self.addCCFlags( '-Wall'.split() )
        self.addCCFlags( '-fno-rtti -fno-exceptions -ffast-math'.split() )
        self.addCCFlags( '-fmessage-length=0 -Wno-trigraphs -Wreturn-type'.split() )
        self.addCCFlags( '-fmacro-backtrace-limit=0 -fdiagnostics-show-note-include-stack'.split() )
        #self.addCCFlags( '-fmodules -gmodules'.split() )
        self.addCCFlags( '-fpascal-strings -fno-common -fstrict-aliasing -g -fembed-bitcode-marker'.split() )
        self.addCCFlags( '-miphoneos-version-min=11.0'.split() )
        self.addCCFlags( ['-isysroot', self.SDK_PATH] )

        self.OBJC_FLAGS= '-fobjc-arc -DOBJC_OLD_DISPATCH_PROTOTYPES=0'.split()

        self.addLibrary( [ 'stdc++', 'pthread', 'm'] )

        self.refresh()


    #--------------------------------------------------------------------------


    def setupCCFlags( self ):

        self.CC_FLAGS_R= []
        table_config= {
                'Debug'   : "-O0 -D_DEBUG -DDEBUG=1",
                'Release' : "-Os -O3 -DNDEBUG",
                'Retail'  : "-Os -O3 -DNDEBUG -DFLB_RETAIL=1",
            }
        self.CC_FLAGS_R.extend( table_config[ self.getConfig() ].split() )
        self.CC_FLAGS_R.extend( self.CC_FLAGS )

        table_arch= {
            'arm7':    '-arch armv7',
            'arm7s':   '-arch armv7s',
            'arm64':   '-arch arm64',
            }
        self.CC_FLAGS_R.extend( table_arch[ self.getTargetArch() ].split() )

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
            base,ext= os.path.splitext( src.lower() )
            if ext == '.m':
                command.extend( '-x objective-c -std=gnu11'.split() )
                command.extend( self.OBJC_FLAGS );
            elif ext == '.mm':
                command.extend( '-x objective-c++ -std=gnu++14 -stdlib=libc++'.split() )
                command.extend( self.OBJC_FLAGS );
            else:
                command.extend( '-x c++ -std=gnu++14 -stdlib=libc++'.split() )
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
        return  [ 'arm64' ]
        #return  [ 'arm64', 'arm7', 'arm7s' ]





