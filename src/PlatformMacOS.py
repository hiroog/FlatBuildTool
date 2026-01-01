# FlatBuildTool 2017/09/15 Hiroyuki Ogasawara
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
        self.CMD_LIPO= 'lipo'
        self.STD= self.getUserOption( 'STD', '20' )

        self.setDefault()


    def summary( self ):
        super().summary()

    def isValid( self ):
        return  self.getHostPlatform() == 'macOS'


    def setDefault( self ):
        self.setTargetPlatform( 'macOS' )

        self.setConfig( 'Debug' )
        self.addCCFlags( '-Wall -fno-rtti -fno-exceptions -ffast-math'.split() )
        self.addCCFlags( '-fmessage-length=0 -pipe -Wno-trigraphs -Wreturn-type -gdwarf-2'.split() )
        self.addCCFlags( ['-DFLB_TARGET_MACOS=1'] )

        self.OBJC_FLAGS= '-fobjc-arc -DOBJC_OLD_DISPATCH_PROTOTYPES=0'.split()

        #self.addLibraries( [ 'stdc++', 'pthread', 'm'] )
        self.addLibraries( [ 'pthread', 'm'] )
        self.addIgnorePaths( [ '/usr/', '/Applications/' ] )

        self.refresh()

    #--------------------------------------------------------------------------

    def getArchFlags( self ):
        sse= self.getUserOption( 'SSE', 'AVX2' )
        avx_opt= ''
        if sse == 'AVX512': ### IceLake
            avx_opt= ' -mavx2 -mfma -mavx512f -mavx512vl -mavx512bw -mavx512dq -mavx512ifma -mavx512vbmi -mavx512vnni -mavx512vbmi2 -mavx512bitalg -mavx512vpopcntdq -mvaes'
        elif sse == 'AVX2': ### Haswell
            avx_opt= ' -mavx2 -mfma'
        table_arch= {
            'x86':   '-arch i386 -m32 -mmmx -msse2 -msse3 -mssse3 -msse4.1 -msse4.2 -maes -mavx -mf16c' + avx_opt,
            'x64':   '-arch x86_64 -m64            -msse3 -mssse3 -msse4.1 -msse4.2 -maes -mavx -mf16c' + avx_opt,
            #'x64':   '-arch x86_64 -m64 -msse3 -mssse3 -msse4.2 -maes',  # Apple M1 x86_64 Rosetta
            'arm64': '-arch arm64',
            'universal': '',
            }
        return  table_arch[ self.getTargetArch() ].split()

    def setupCCFlags( self ):

        self.CC_FLAGS_R= []
        table_config= {
                'Debug'   : "-O0 -D_DEBUG -DDEBUG=1",
                'Release' : "-Os -O3 -DNDEBUG",
                'Retail'  : "-Os -O3 -DNDEBUG -DFLB_RETAIL=1",
            }
        self.CC_FLAGS_R.extend( table_config[ self.getConfig() ].split() )
        self.CC_FLAGS_R.extend( self.getArchFlags() )

        for inc in self.INCLUDE_PATH_R:
            #print( 'INCLUDE=' + inc )
            self.CC_FLAGS_R.append( '-I' + inc )
        self.CC_FLAGS_R.extend( self.CC_FLAGS )

    def setupLinkFlags( self ):
        super().setupLinkFlags()
        self.LINK_FLAGS_R.extend( self.getArchFlags() )

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
                command.extend( self.OBJC_FLAGS )
            elif ext == '.mm':
                command.extend( '-x objective-c++ -stdlib=libc++'.split() )
                command.extend( ['-std=c++'+self.STD] )
                command.extend( self.OBJC_FLAGS )
            else:
                command.extend( '-x c++ -stdlib=libc++'.split() )
                command.extend( ['-std=c++'+self.STD] )
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

    def getBuildCommand_Dll( self, target, src_list ):
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

    def getBuildCommand_Lipo( self, target, src_list ):
        command= []
        command.append( self.CMD_LIPO )
        command.append( '-create' )
        command.append( '-output' )
        command.append( target )
        for src in src_list:
            command.append( src )
        return  command

    #--------------------------------------------------------------------------
    # macOS Intel   : x64 (x86)
    # macOS Apple M1: arm64

    def getSupportArchList( self ):
        return  [ 'x64', 'arm64' ]


