# FlatBuildTool 2017/07/24 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  PlatformWindows
import  PlatformLinux
import  PlatformMacOS
import  PlatformAndroid
import  PlatformCS
#import  PlatformIOS
#import  PlatformTVOS
#import  PlatformWatchOS

tool.addPlatform( 'Windows',    PlatformWindows )
tool.addPlatform( 'Android',    PlatformAndroid )
tool.addPlatform( 'Linux',      PlatformLinux )
tool.addPlatform( 'macOS',      PlatformMacOS )
tool.addPlatform( 'CS',         PlatformCS )
#tool.addPlatform( 'iOS',       PlatformIOS )
#tool.addPlatform( 'tvOS',      PlatformTVOS )
#tool.addPlatform( 'watchOS',   PlatformWatchOS )


