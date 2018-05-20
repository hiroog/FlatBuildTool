# FlatBuildTool 2017/07/24 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  PlatformWindows
import  PlatformLinux
import  PlatformAndroid
import  PlatformMacOS
import  PlatformIOS
import  PlatformCS
#import  PlatformTVOS
#import  PlatformWatchOS

tool.addPlatform( 'Windows',    PlatformWindows )
tool.addPlatform( 'Linux',      PlatformLinux )
tool.addPlatform( 'Android',    PlatformAndroid )
tool.addPlatform( 'macOS',      PlatformMacOS )
tool.addPlatform( 'iOS',        PlatformIOS )
tool.addPlatform( 'CS',         PlatformCS )
#tool.addPlatform( 'tvOS',      PlatformTVOS )
#tool.addPlatform( 'watchOS',   PlatformWatchOS )


