# FlatBuildTool 2017/07/26 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  re
import  PlatformCommon
import  BuildUtility
from BuildUtility import Log


#   P   27  Android 9.0?
#   O   26  Android 8.0
#   N   25  Android 7.1
#   N   24  Android 7.0     Daydream
#   M   23  Android 6.0
#   L   22  Android 5.1
#   L   21  Android 5.0     GLES3.1 64bit
#   K   20  Android 4.4W
#   K   19  Android 4.4
#   J   18  Android 4.3     GLES3.0
#   J   17  Android 4.2
#   J   16  Android 4.1
#   I   15  Android 4.0.3
#   I   14  Android 4.0



class TargetEnvironment( PlatformCommon.TargetEnvironmentCommon ):

    def __init__( self, tool, parent= None ):
        super().__init__( tool, parent )

        self.NDK_ROOT= tool.getEnv( 'FLB_NDK_ROOT', tool.getEnv( 'NDK_ROOT' ) )
        if self.NDK_ROOT is None:
            return

        #self.NDK_ROOT= tool.getEnv( 'NDK_ROOT' )
        if not os.path.exists( self.NDK_ROOT ):
            raise BuildUtility.FLB_Error( 'NDK not found ($NDK_ROOT=%s)' % self.NDK_ROOT )

        self.CMD_CC= 'clang++'
        self.CMD_LINK= 'clang++'
        self.CMD_LIB= 'ar'

        self.GCC_VERSION= '4.9'
        self.API_LEVEL= 24
        self.NDK_VERSION= self.getNDKVersion()
        #print( 'NDK_VERSION = ' + str(self.NDK_VERSION) )

        self.setDefault()


    def summary( self ):
        super().summary()
        print( 'NDK_ROOT = ' + self.NDK_ROOT )
        print( 'GCC_VERSION = ' + self.GCC_VERSION )
        print( 'NDK_VERSION = ' + str(self.NDK_VERSION) )


    def isValid( self ):
        return  self.NDK_ROOT is not None


    def getNDKVersion( self ):
        with open( os.path.join( self.NDK_ROOT, 'source.properties' ) ) as fi:
            revision_pat= re.compile( r'^Pkg\.Revision\s*=\s*([0-9]+)\.([0-9]+)' )
            for line in fi:
                pat= revision_pat.search( line )
                if pat != None:
                    return  int( pat.group( 1 ) )
        raise FLB_Error( 'Android NDK invalid version' )
        return  0

    def setApiLevel( self, level ):
        self.API_LEVEL= level

    def getAndroidPlatform( self ):
        return  'Android-' + str(self.API_LEVEL)


    def setDefault( self ):
        host_platform_name= self.getHostPlatformName()
        if host_platform_name == None:
            raise BuildUtility.FLB_Error( 'Android toolchain path not found' )
        self.HOST_TOOLCHAIN_NAME=host_platform_name
        self.LLVM_TOOLCHAIN_ROOT= os.path.join( self.NDK_ROOT, 'toolchains/llvm/prebuilt', host_platform_name )

        self.CMD_CC= os.path.join( self.LLVM_TOOLCHAIN_ROOT, 'bin/clang++' )
        self.CMD_LINK= self.CMD_CC
        self.CMD_LIB= self.CMD_CC


        self.setConfig( 'Debug' )
        self.addCCFlags( '-fpic -ffunction-sections -funwind-tables -fstack-protector-strong'.split() )
#        self.addCCFlags( '-Wno-invalid-command-line-argument -Wno-unused-command-line-argument'.split() )
        self.addCCFlags( '-no-canonical-prefixes'.split() )
#        self.addCCFlags( '-no-canonical-prefixes -fno-integrated-as'.split() )
        self.addCCFlags( '-Wall'.split() )
        self.addCCFlags( '-std=gnu++14 -fno-rtti -fno-exceptions -ffast-math'.split() )
        self.addCCFlags( '-Wa,--noexecstack -Wformat -Werror=format-security'.split() )
        self.addCCFlags( '-fmessage-length=0 -pipe -Wno-trigraphs -Wreturn-type'.split() )
#        self.addCCFlags( '-gdwarf-2'.split() )
        self.addCCFlags( '-fno-diagnostics-color'.split() )

        self.addIncludePath( [
                    #os.path.join( self.NDK_ROOT, 'sources/cxx-stl/stlport/stlport' ),
                    #os.path.join( self.NDK_ROOT, 'sources/cxx-stl/system/include' ),
                    os.path.join( self.NDK_ROOT, 'sources/cxx-stl/llvm-libc++/libcxx/include' ),
                    #os.path.join( self.NDK_ROOT, 'sources/cxx-stl/gnu-libstdc++/4.9/include' ),
                    #os.path.join( self.NDK_ROOT, 'sources/cxx-stl/gabi++/include' ),
                ] )

        self.addLibrary( [ 'stdc++', 'pthread', 'm'] )

        self.refresh()


    #--------------------------------------------------------------------------

    def getHostPlatformName( self ):
        host_toolchain_table= {
                        'Windows' :
                            {
                                'x64' : 'windows-x86_64',
                                'x86' : 'windows-x86',
                            },
                        'Linux' :
                            {
                                'x64' : 'linux-x86_64',
                            },
                        'macOS' :
                            {
                                'x64' : 'darwin-x86_64',
                            }
                    }

        host_platform_name= None
        if self.getHostPlatform() in host_toolchain_table:
            table= host_toolchain_table[ self.getHostPlatform() ]
            if self.getHostArch() in table:
                host_platform_name= table[ self.getHostArch() ]
        return  host_platform_name



    def getTargetArchName( self ):
        target_arch_name_table= {
                    'arm5'   :   'arm-linux-androideabi',
                    'arm7'   :   'arm-linux-androideabi',
                    'arm7hf' :   'arm-linux-androideabi',
                    'arm64'  :   'aarch64-linux-android',
                    'x86'    :   'i686-linux-android',
                    'x64'    :   'x86_64-linux-android',
                    'mips'   :   'mipsel-linux-android',
                    'mips64' :   'mips64el-linux-android',
                }
        if self.getTargetArch() in target_arch_name_table:
            return  target_arch_name_table[ self.getTargetArch() ]
        return  None


    def getGCCCommandPrefix( self ):
        target_gcc_prefix_table= {
                    'arm5'   :   'arm-linux-androideabi-',
                    'arm7'   :   'arm-linux-androideabi-',
                    'arm7hf' :   'arm-linux-androideabi-',
                    'arm64'  :   'aarch64-linux-android-',
                    'x86'    :   'i686-linux-android-',
                    'x64'    :   'x86_64-linux-android-',
                    'mips'   :   'mipsel-linux-android-',
                    'mips64' :   'mips64el-linux-android-',
                }
        if self.getTargetArch() in target_gcc_prefix_table:
            return  target_gcc_prefix_table[ self.getTargetArch() ]
        return  None


    def getGCCPrefix( self ):
        target_gcc_prefix_table= {
                    'arm5'   :   'arm-linux-androideabi-',
                    'arm7'   :   'arm-linux-androideabi-',
                    'arm7hf' :   'arm-linux-androideabi-',
                    'arm64'  :   'aarch64-linux-android-',
                    'x86'    :   'x86-',
                    'x64'    :   'x86_64-',
                    'mips'   :   'mipsel-linux-android-',
                    'mips64' :   'mips64el-linux-android-',
                }
        if self.getTargetArch() in target_gcc_prefix_table:
            return  target_gcc_prefix_table[ self.getTargetArch() ]
        return  None


    def setupBinPath( self ):
        super().setupBinPath()
        self.CMD_LIB= os.path.join( self.GCC_TOOLCHAIN_ROOT, 'bin', self.getGCCCommandPrefix() + 'ar' )


    def setupCCFlags( self ):
        self.CC_FLAGS_R= []

        #target_gcc_prefix= self.getGCCPrefix()
        #gcc_toolchain_name= target_gcc_prefix + self.GCC_VERSION
        #self.GCC_TOOLCHAIN_ROOT= os.path.join( self.NDK_ROOT, 'toolchains', gcc_toolchain_name, 'prebuilt', self.HOST_TOOLCHAIN_NAME )

        self.CC_FLAGS_R.append( '-gcc-toolchain' )
        self.CC_FLAGS_R.append( self.GCC_TOOLCHAIN_ROOT )


        target_isystem_table= {
                'arm5'      : 'arch-arm',
                'arm7'      : 'arch-arm',
                'arm7hf'    : 'arch-arm',
                'arm64'     : 'arch-arm64',
                'x86'       : 'arch-x86',
                'x64'       : 'arch-x86_64',
                'mips'      : 'arch-mips',
                'mips64'    : 'arch-mips64',
            }
        isystem_arch= None
        if self.getTargetArch() in target_isystem_table:
            isystem_arch= target_isystem_table[ self.getTargetArch() ]

        self.CC_FLAGS_R.append( '--sysroot' )
        self.CC_FLAGS_R.append( os.path.join( self.NDK_ROOT, 'sysroot' ) )

        if self.NDK_VERSION >= 15:
            self.ISYSTEM_ROOT= os.path.join( self.NDK_ROOT, 'sysroot' )
            self.CC_FLAGS_R.append( '-isystem' )
            self.CC_FLAGS_R.append( os.path.join( self.ISYSTEM_ROOT, 'usr/include', self.getTargetArchName() ) )
        else:
            self.ISYSTEM_ROOT= os.path.join( self.NDK_ROOT, 'platforms', self.getAndroidPlatform().lower(), isystem_arch )
            self.CC_FLAGS_R.append( '-isystem' )
            self.CC_FLAGS_R.append( os.path.join( self.ISYSTEM_ROOT, 'usr/include' ) )




        table_config= {
                'Debug'   : "-O0 -g -D_DEBUG",
                'Release' : "-Os -g -O3 -DNDEBUG",
                'Retail'  : "-Os -g -O3 -DNDEBUG -DFLB_RETAIL=1",
            }
        self.CC_FLAGS_R.extend( table_config[ self.getConfig() ].split() )
        self.CC_FLAGS_R.extend( self.CC_FLAGS )
        self.CC_FLAGS_R.append( '-DANDROID' )
        self.CC_FLAGS_R.append( '-D__ANDROID_API__=%d' % self.API_LEVEL )



        target_arch_table= {
            'x86':    'i686-none-linux-android',
            'x64':    'x86_64-none-linux-android',
            'arm7':   'armv7-none-linux-androideabi',
            'arm7hf': 'armv7-none-linux-androideabi',
            'arm5':   'armv5te-none-linux-androideabi',
            'arm64':  'aarch64-none-linux-android',
            'mips':   'mipsel-none-linux-android',
            'mips64': 'mips64el-none-linux-android',
            }
        target_arch_option_table= {
            'x86':    '-msse -msse2 -msse3 -mssse3 -fPIC',
            'x64':    '-msse -msse2 -msse3 -mssse3 -msse4.1 -msse4.2 -maes -fPIC',
            'arm7':   '-march=armv7-a -marm -mfpu=vfpv3-d16',
            'arm7hf': '-march=armv7-a -marm -mfpu=vfpv3-d16 -mfloat-abi=hard -mhard-float',
#            'arm7hf': '-march=armv7-a -marm -mfpu=vfpv3-d16 -mfloat-abi=hard -mhard-float -D_NDK_MATH_NO_SOFTFP=1',
            'arm5':   '-march=armv5te -mtune=xscale -msoft-float -marm',
            'arm64':  '',
            'mips':   '-mips32 -fintegrated-as',
            'mips64': '-fintegrated-as',
            }
        target_arch= target_arch_table[ self.getTargetArch() ]
        #if self.NDK_VERSION >= 15:
        #    target_arch+= str(self.API_LEVEL)

        self.CC_FLAGS_R.append( '-fpic' )

        self.CC_FLAGS_R.append( '-target' )
        self.CC_FLAGS_R.append( target_arch )
        self.CC_FLAGS_R.extend( target_arch_option_table[ self.getTargetArch() ].split() )

        for inc in self.INCLUDE_PATH_R:
            #print( 'INCLUDE=' + inc )
            self.CC_FLAGS_R.append( '-I' + inc )


    def refresh( self ):
        self.setTargetPlatform( 'Android' + str(self.API_LEVEL) )

        target_gcc_prefix= self.getGCCPrefix()
        gcc_toolchain_name= target_gcc_prefix + self.GCC_VERSION
        self.GCC_TOOLCHAIN_ROOT= os.path.join( self.NDK_ROOT, 'toolchains', gcc_toolchain_name, 'prebuilt', self.HOST_TOOLCHAIN_NAME )

        super().refresh()


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
        if True:
            if self.API_LEVEL >= 21:
                return  [ 'arm7', 'arm64', 'x86', 'x64' ]
            else:
                return  [ 'arm7', 'x86' ]
        else:
            if self.API_LEVEL >= 21:
                return  [ 'arm7', 'arm7hf', 'arm64', 'arm5', 'x86', 'x64', 'mips', 'mips64' ]
            else:
                return  [ 'arm7', 'arm5', 'x86', 'mips' ]









