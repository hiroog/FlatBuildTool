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

        self.SDK_VERSION='14.2'

        self.CMD_CC= '/usr/bin/clang++'
        self.CMD_LINK= '/usr/bin/clang++'
        self.CMD_LIB= 'ar'
        self.STD= self.getUserOption( 'STD', '17' )

        self.setDefault()


    def summary( self ):
        super().summary()

    def isValid( self ):
        return  self.getHostPlatform() == 'macOS'


    def setDefault( self ):
        self.setTargetPlatform( 'iOS' )
        self.setTargetArch( 'arm64e' )
        self.SDK_PATH= '/Applications/Xcode.app/Contents/Developer/Platforms/iPhoneOS.platform/Developer/SDKs/iPhoneOS.sdk'

        self.setConfig( 'Debug' )
        self.addCCFlags( '-Wall -fno-rtti -fno-exceptions -ffast-math'.split() )
        self.addCCFlags( '-fmessage-length=0 -Wno-trigraphs -Wreturn-type'.split() )
        self.addCCFlags( '-fmacro-backtrace-limit=0 -fdiagnostics-show-note-include-stack'.split() )
        #self.addCCFlags( '-fmodules -gmodules'.split() )
        self.addCCFlags( '-fpascal-strings -fno-common -fstrict-aliasing -g -fembed-bitcode-marker'.split() )
        self.addCCFlags( ['-miphoneos-version-min='+self.SDK_VERSION ] )
        self.addCCFlags( ['-isysroot', self.SDK_PATH] )

        self.OBJC_FLAGS= '-fobjc-arc -DOBJC_OLD_DISPATCH_PROTOTYPES=0'.split()

        self.addLibraries( [ 'stdc++', 'pthread', 'm'] )

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

        table_arch= {
            'arm7':     '-arch armv7',    # vfpv3
            'arm7s':    '-arch armv7s',   # vfpv4
            'arm7k':    '-arch armv7k',   # 64bit armv7a
            'arm64_32': '-arch arm64_32', # armv8a
            'arm64':    '-arch arm64',    # armv8a
            'arm64e':   '-arch arm64e',   # armv8.3a
            }
        self.CC_FLAGS_R.extend( table_arch[ self.getTargetArch() ].split() )

        for inc in self.INCLUDE_PATH_R:
            #print( 'INCLUDE=' + inc )
            self.CC_FLAGS_R.append( '-I' + inc )
        self.CC_FLAGS_R.extend( self.CC_FLAGS )

    #--------------------------------------------------------------------------

    def getDllName( self, lib_name ):
        return  'lib' + lib_name + '.dylib'

    #--------------------------------------------------------------------------

    def getBuildCommand_CC( self, target, src_list ):
        command= []
        command.append( self.CMD_CC )
        command.append( '-c' )
        command.extend( self.CC_FLAGS_R )
        for src in src_list:
            base,ext= os.path.splitext( src.lower() )
            if ext == '.m':
                command.extend( '-x objective-c -std=gnu17'.split() )
                command.extend( self.OBJC_FLAGS );
            elif ext == '.mm':
                command.extend( '-x objective-c++ -stdlib=libc++'.split() )
                command.extend( ['-std=c++'+self.STD] )
                command.extend( self.OBJC_FLAGS );
            else:
                command.extend( '-x c++ -stdlib=libc++'.split() )
                command.extend( ['-std=gnu++'+self.STD] )
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

    def getBuildCommand_Link( self, target, src_list ):
        command= []
        command.append( self.CMD_CC )
        command.append( '-dynamiclib' )
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
    # iOS/iPadOS: arm64e arm64 (arm7s, arm7, arm6)
    # watchOS:    arm64_32 arm7k
    #  armv7s = Apple A6(vfpv4)
    #  arm64  = Apple A7(armv8a)
    #  arm64e = Apple A12(armv8.3a)
    #  armv7k = Apple S1(armv7a)
    #  arm64_32 = Apple S4(armv8.3a)

    def getSupportArchList( self ):
        return  [ 'arm64', 'arm64e' ]
        #return  [ 'arm64', 'arm64e', 'arm7', 'arm7s' ]
        #return  [ 'arm64', 'arm64e', 'arm7', 'arm7s', 'x64', 'x86', 'arm7k', 'arm64_32' ]


