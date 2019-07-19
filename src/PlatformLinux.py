# FlatBuildTool 2017/07/23 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  PlatformCommon
import  BuildUtility
from BuildUtility import Log


class TargetEnvironment( PlatformCommon.TargetEnvironmentCommon ):

    def __init__( self, tool, parent= None ):
        super().__init__( tool, parent )

        self.CMD_CC= 'clang'
        self.CMD_LINK= 'clang'
        self.CMD_LIB= 'ar'

        if self.isTermux():
            if self.getHostArch() == 'arm7':
                self.ARM7ABI= 'softfp'

        # --opt ARM7ABI=hard
        # --opt ARM7ABI=softfp
        # --opt ARM7ABI=soft
        # or 'ARM7ABI hard' in local_config.txt
        self.ARM7ABI= 'hard'
        if 'ARM7ABI' in self.tool.global_env.USER_OPTION:
            self.ARM7ABI= self.tool.global_env.USER_OPTION['ARM7ABI']
        # --opt ARM7FP=neon
        # --opt ARM7FP=vfpv3-d16
        # --opt ARM7FP=neon-vfpv4
        # or 'ARM7FP neon-vfpv4' in local_config.txt
        self.ARM7FP= 'neon'
        if 'ARM7FP' in self.tool.global_env.USER_OPTION:
            self.ARM7FP= self.tool.global_env.USER_OPTION['ARM7FP']
        # --opt HOST_ARCH=x86
        # or 'HOST_ARCH x86' in local_config.txt
        if 'HOST_ARCH' in self.tool.global_env.USER_OPTION:
            host_arch= self.tool.global_env.USER_OPTION['HOST_ARCH']
            self.setHostArch( host_arch )
            self.setTargetArch( host_arch )


        self.setDefault()


    def summary( self ):
        super().summary()

    def isValid( self ):
        return  True

    def isTermux( self ):
        if 'HOME' in os.environ:
            if 'com.termux' in os.environ['HOME']:
                return  True
        return  False

    def setDefault( self ):
        self.setTargetPlatform( 'Linux' )

        self.setConfig( 'Debug' )
        self.addCCFlags( '-fpic -Wall -std=gnu++1z -fno-rtti -fno-exceptions -ffast-math'.split() )
        #self.addCCFlags( '-Wall -std=c++14 -fno-rtti -fno-exceptions -ffast-math'.split() )
        self.addCCFlags( '-fmessage-length=0 -pipe -Wno-trigraphs -Wreturn-type -gdwarf-2 -DFLB_FORCE_LINUX=1 -DFLB_TARGET_LINUX=1'.split() )
        #self.addCCFlags( '-funwind-tables -fstack-protector-strong -no-canonical-prefixes'.split() )

        self.addLibraries( [ 'stdc++', 'pthread', 'm'] )

        self.refresh()


    #--------------------------------------------------------------------------


    def setupCCFlags( self ):

        self.CC_FLAGS_R= []
        table_config= {
                'Debug'   : "-O0 -g -D_DEBUG",
                'Release' : "-Os -g -O3 -DNDEBUG",
                'Retail'  : "-Os -O3 -DNDEBUG -DFLB_RETAIL=1",
            }
        self.CC_FLAGS_R.extend( table_config[ self.getConfig() ].split() )

        table_arch= {
            'x86':   '-m32 -msse -msse2 -msse3 -mssse3 -maes',
            'x64':   '-m64 -msse -msse2 -msse3 -mssse3 -msse4.1 -msse4.2 -maes',
            'arm7':  '-march=armv7-a -fPIC -marm -mfpu=%s -mfloat-abi=%s' % (self.ARM7FP, self.ARM7ABI),
            'arm6':  '-march=armv6 -marm -mfpu=vfp -mfloat-abi=hard',
            'arm64': '-march=armv8-a+crypto',
            #'arm64': '-march=armv8.2-a+crypto+fp16',
            #'arm64': '-march=armv8-a+crypto -mfpu=crypto-neon-fp-armv8',
            }
        self.CC_FLAGS_R.extend( table_arch[ self.getTargetArch() ].split() )

        for inc in self.INCLUDE_PATH_R:
            #print( 'INCLUDE=' + inc )
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









