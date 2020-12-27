# FlatBuildTool 2020/12/27 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

#import  os
#import  PlatformCommon
#import  BuildUtility
#from BuildUtility import Log
import	PlatformIOS

class TargetEnvironment( PlatformIOS.TargetEnvironment ):

    def __init__( self, tool, parent= None ):
        super().__init__( tool, parent )

    def setDefault( self ):
        self.SDK_VERSION='6.2'
        self.setTargetPlatform( 'watchOS' )
        self.setTargetArch( 'arm64_32' )
        self.SDK_PATH= '/Applications/Xcode.app/Contents/Developer/Platforms/WatchOS.platform/Developer/SDKs/WatchOS.sdk'

        self.setConfig( 'Debug' )
        self.addCCFlags( '-Wall -fno-rtti -fno-exceptions -ffast-math'.split() )
        self.addCCFlags( '-fmessage-length=0 -Wno-trigraphs -Wreturn-type'.split() )
        self.addCCFlags( '-fmacro-backtrace-limit=0 -fdiagnostics-show-note-include-stack'.split() )
        #self.addCCFlags( '-fmodules -gmodules'.split() )
        self.addCCFlags( '-fpascal-strings -fno-common -fstrict-aliasing -g -fembed-bitcode-marker'.split() )
        self.addCCFlags( ['-mwatchos-version-min='+self.SDK_VERSION ] )
        self.addCCFlags( ['-isysroot', self.SDK_PATH] )

        self.OBJC_FLAGS= '-fobjc-arc -DOBJC_OLD_DISPATCH_PROTOTYPES=0'.split()

        self.addLibraries( [ 'stdc++', 'pthread', 'm'] )

        self.refresh()

    def getSupportArchList( self ):
        return  [ 'arm7k', 'arm64_32' ]


