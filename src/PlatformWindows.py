# FlatBuildTool 2017/07/21 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  platform
import  PlatformCommon
import  BuildUtility
from BuildUtility import Log

if platform.system() == 'Windows':
    import  winreg


class TargetEnvironment( PlatformCommon.TargetEnvironmentCommon ):

    def __init__( self, tool, parent= None ):
        super().__init__( tool, parent )

        #self.X86_PROGRAMFILES= 'C:/Program Files'
        self.MSVC_DIR= None
        self.WINDOWS_SDK_DIR= None
        self.WINDOWS_SDK_VERSION= None

        self.CMD_CC= None
        self.CMD_LINK= None
        self.CMD_LIB= None

        self.SAVE_PATH= os.environ[ 'PATH' ]

        self.findVSPath()
        if self.MSVC_DIR is None:
            return

        self.setDefault()

        self.ARCH_LIST= [ 'x64', 'x86' ]
        if os.path.exists( os.path.join( self.MSVC_VC_DIR, 'bin/HostX64/arm64' ) ):
            self.ARCH_LIST.append( 'arm64' )
        if os.path.exists( os.path.join( self.MSVC_VC_DIR, 'bin/HostX64/arm' ) ):
            self.ARCH_LIST.append( 'arm7' )

        Log.d( 'MSVC = %d' % self.MSVC_VERSION )
        Log.d( 'SDK = ', self.WINDOWS_SDK_DIR )
        Log.d( 'SDK Version = ', self.WINDOWS_SDK_VERSION )
        Log.d( 'CPU Arch    = ', ','.join(self.ARCH_LIST) )


    def summary( self ):
        super().summary()
        Log.p( 'MSVC = %d' % self.MSVC_VERSION )
        Log.p( 'SDK = ', self.WINDOWS_SDK_DIR )
        Log.p( 'SDK Version = ', self.WINDOWS_SDK_VERSION )
        Log.p( 'CPU Arch    = ', ','.join(self.ARCH_LIST) )


    def isValid( self ):
        return  self.MSVC_DIR is not None


    def findVSFromDir( self, version ):
        if self.getHostArch() == 'x64':
            X86_PROGRAMFILES= os.environ['ProgramFiles(x86)']
        else:
            X86_PROGRAMFILES= os.environ['ProgramFiles']
        vc_search_path= [
                os.path.join( X86_PROGRAMFILES, 'Microsoft Visual Studio', version, 'Professional/VC' ),
                os.path.join( X86_PROGRAMFILES, 'Microsoft Visual Studio', version, 'Community/VC' ),
                os.path.join( X86_PROGRAMFILES, 'Microsoft Visual Studio', version, 'Preview/VC' ),
            ]
        path= self.findPath( vc_search_path )
        if path is not None:
            return  os.path.dirname( path )
        return  None


    def findVSDir( self, version ):
        try:
            with winreg.OpenKey( winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\WOW6432Node\\Microsoft\\VisualStudio\\SxS\\VS7' ) as key:
                return  winreg.QueryValueEx( key, version )[0]
            with winreg.OpenKey( winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\Microsoft\\VisualStudio\\SxS\\VS7' ) as key:
                return  winreg.QueryValueEx( key, version )[0]
            with winreg.OpenKey( winreg.HKEY_CURRENT_USER, 'SOFTWARE\\Wow6432Node\\Microsoft\\VisualStudio\\SxS\\VS7' ) as key:
                return  winreg.QueryValueEx( key, version )[0]
            with winreg.OpenKey( winreg.HKEY_CURRENT_USER, 'SOFTWARE\\Microsoft\\VisualStudio\\SxS\\VS7' ) as key:
                return  winreg.QueryValueEx( key, version )[0]
        except OSError:
            return  None

    def findSDKDir( self, version, keyname ):
        try:
            with winreg.OpenKey( winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\WOW6432Node\\Microsoft\\Microsoft SDKs\\Windows\\' + version ) as key:
                return  winreg.QueryValueEx( key, 'InstallationFolder' )[0]
            with winreg.OpenKey( winreg.HKEY_CURRENT_USER, 'SOFTWARE\\Wow6432Node\\Microsoft\\Microsoft SDKs\\Windows\\' + version ) as key:
                return  winreg.QueryValueEx( key, 'InstallationFolder' )[0]
            with winreg.OpenKey( winreg.HKEY_LOCAL_MACHINE, 'SOFTWARE\\WOW6432Node\\Microsoft\\Windows Kits\\Installed Roots' ) as key:
                return  winreg.QueryValueEx( key, keyname )[0]
            with winreg.OpenKey( winreg.HKEY_CURRENT_USER, 'SOFTWARE\\Wow6432Node\\Microsoft\\Windows Kits\\Installed Roots' ) as key:
                return  winreg.QueryValueEx( key, keyname )[0]
        except OSError:
            return  None


    def findVSPath( self ):

        # --opt VC=20xx
        # or 'VC 20xx' in local_config.txt
        vc= int(self.getUserOption( 'VC', '2099' ))

        if vc >= 2019:
            path= self.findVSDir( '16.0' )
            if path is not None:
                self.MSVC_DIR= path
                self.MSVC_VERSION= 2019
                return
            else:
                path= self.findVSFromDir( '2019' )
                if path is not None:
                    self.MSVC_DIR= path
                    self.MSVC_VERSION= 2019
                    return

        if vc >= 2017:
            path= self.findVSDir( '15.0' )
            if path is not None:
                self.MSVC_DIR= path
                self.MSVC_VERSION= 2017
                return

        path= self.findVSDir( '14.0' )
        if path is not None:
            self.MSVC_DIR= path
            self.MSVC_VERSION= 2015
            return

    def findSDKPath( self ):
        path= self.findSDKDir( 'v10.0', 'KitsRoot10' )
        if path is not None:
            self.WINDOWS_SDK_DIR= path
            return
        path= self.findSDKDir( 'v8.1', 'KitsRoot81' )
        if path is not None:
            self.WINDOWS_SDK_DIR= path
            return


    def setDefault( self ):

        self.findSDKPath()

        #self.WINDOWS_SDK_DIR= self.findPath( [
        #                    os.path.join( self.X86_PROGRAMFILES, 'Windows Kits\\10' ),
        #                    os.path.join( self.X86_PROGRAMFILES, 'Windows Kits\\8.1' ),
        #                ] )
        self.WINDOWS_SDK_VERSION= sorted( os.listdir( os.path.join( self.WINDOWS_SDK_DIR, 'Include' ) ), reverse= True )[0]
        #self.WINDOWS_SDK_VERSION= '10.0.14393.0'

        self.MSVC_VC_DIR= self.getVCRoot()


        self.addCCFlags( '-W3 -WX -GA -GF -Gy -Zi -EHsc -fp:except- -fp:fast -DWIN32 -D_WINDOWS -nologo -Zc:forScope,wchar_t,auto -utf-8'.split() )
        cstd= self.getUserOption( 'STD', '17' )
        self.addCCFlags( ['-std:c++'+cstd] )
        self.addCCFlags( ['-DFLB_TARGET_WINDOWS=1'] )

        self.addLibFlags( ['-nologo'] )
        self.addLinkFlags( ['-nologo'] )

        self.refresh()


    def getVCRoot( self ):
        if self.MSVC_VERSION >= 2017:
            vc_root= os.path.join( self.MSVC_DIR, 'VC/Tools/MSVC' )
            vc_version= sorted( os.listdir( vc_root ), reverse= True )[0]
            return  os.path.join( vc_root, vc_version )
        else:
            return  os.path.join( self.MSVC_DIR, 'VC' )

    #--------------------------------------------------------------------------

    def setupBinPath( self ):

        self.BIN_PATH_R= []
        self.BIN_PATH_R.extend( self.BIN_PATH )

        if self.MSVC_VERSION >= 2017:

            if self.getHostArch() == 'x64':
                if self.getTargetArch() == 'x64':
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX64/x64' ) )
                elif self.getTargetArch() == 'x86':
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX64/x86' ) )
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX64/x64' ) )
                elif self.getTargetArch() == 'arm7':
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX64/arm' ) )
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX64/x64' ) )
                elif self.getTargetArch() == 'arm64':
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX64/arm64' ) )
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX64/x64' ) )
            else:
                if self.getTargetArch() == 'x64':
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX86/x64' ) )
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX86/x86' ) )
                elif self.getTargetArch() == 'x86':
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX86/x86' ) )
                elif self.getTargetArch() == 'arm7':
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX86/arm' ) )
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX86/x86' ) )
                elif self.getTargetArch() == 'arm64':
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX86/arm64' ) )
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/HostX86/x86' ) )

        elif self.MSVC_VERSION == 2015:

            if self.getHostArch() == 'x64':
                if self.getTargetArch() == 'x64':
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/amd64' ) )
                else:
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/amd64_x86' ) )
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/amd64' ) )
            else:
                if self.getTargetArch() == 'x64':
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin/x86_amd64' ) )
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin' ) )
                else:
                    self.BIN_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'bin' ) )

        else:
            raise   BuildUtility.FLB_Error( 'VC unsupported version' )

        self.BIN_PATH_R.append( os.path.join( self.MSVC_DIR, 'Common7/IDE' ) )

        self.CMD_CC= self.searchCommandPath( 'cl.exe' )
        self.CMD_LINK= self.searchCommandPath( 'link.exe' )
        self.CMD_LIB= self.searchCommandPath( 'lib.exe' )

        if self.CMD_CC == None:
            raise   BuildUtility.FLB_Error( 'cl.exe not found' )

        path_r= ''
        for path in self.BIN_PATH_R:
            path_r+= path + ';'
        os.environ[ 'PATH' ]= path_r + self.SAVE_PATH
        #print( 'PATH=' + str(os.environ['PATH']) )


    def setupIncludePath( self ):
        self.INCLUDE_PATH_R= []
        self.INCLUDE_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'include' ) )
        self.INCLUDE_PATH_R.append( os.path.join( self.WINDOWS_SDK_DIR, 'Include', self.WINDOWS_SDK_VERSION, 'shared' ) )
        self.INCLUDE_PATH_R.append( os.path.join( self.WINDOWS_SDK_DIR, 'Include', self.WINDOWS_SDK_VERSION, 'um' ) )
        self.INCLUDE_PATH_R.append( os.path.join( self.WINDOWS_SDK_DIR, 'Include', self.WINDOWS_SDK_VERSION, 'ucrt' ) )
        self.INCLUDE_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'atlmfc/include' ) )
        self.INCLUDE_PATH_R.extend( self.INCLUDE_PATH )


    def setupLibPath( self ):
        self.LIB_PATH_R= []

        if self.MSVC_VERSION >= 2017:

            if self.getTargetArch() == 'x64':
                self.LIB_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'lib/x64' ) )
            elif self.getTargetArch() == 'x86':
                self.LIB_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'lib/x86' ) )
            elif self.getTargetArch() == 'arm7':
                self.LIB_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'lib/arm' ) )
            elif self.getTargetArch() == 'arm64':
                self.LIB_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'lib/arm64' ) )


        elif self.MSVC_VERSION == 2015:

            if self.getTargetArch() == 'x64':
                self.LIB_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'lib/amd64' ) )
                self.LIB_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'lib' ) )
            elif self.getTargetArch() == 'arm7':
                self.LIB_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'lib/arm' ) )
                self.LIB_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'lib' ) )
            else:
                self.LIB_PATH_R.append( os.path.join( self.MSVC_VC_DIR, 'lib' ) )


        sdk_arch= { 'x64' : 'x64', 'x86' : 'x86', 'arm7' : 'arm', 'arm64' : 'arm64' }[ self.getTargetArch() ]
        self.LIB_PATH_R.append( os.path.join( self.WINDOWS_SDK_DIR, 'lib', self.WINDOWS_SDK_VERSION, 'um', sdk_arch ) )
        self.LIB_PATH_R.append( os.path.join( self.WINDOWS_SDK_DIR, 'lib', self.WINDOWS_SDK_VERSION, 'ucrt', sdk_arch ) )
        self.LIB_PATH_R.extend( self.LIB_PATH )


    def setupCCFlags( self ):

        self.CC_FLAGS_R= []
        table_config= {
                'Debug'   : "-D_DEBUG -MDd -Od",
                'Release' : "-DNDEBUG -MD -O2 -Oi -Ot -Ob2",
                'Retail'  : "-DNDEBUG -MD -O2 -Oi -Ot -Ob2 -DFLB_RETAIL=1",
            }
        self.CC_FLAGS_R.extend( table_config[ self.getConfig() ].split() )
        self.CC_FLAGS_R.append( '-Fd' + self.getOutputPath( self.OUTPUT_OBJ_DIR, 'vc.pdb'  ) )
        self.CC_FLAGS_R.append( '-FS' )

        # --opt SSE=AVX
        sse= self.getUserOption( 'SSE', 'AVX2' )
        table_arch= {
                'x64'   : '-arch:'+sse+' -favor:blend',
                'x86'   : '-arch:'+sse+' -favor:blend',
                'arm7'  : '-arch:VFPv4',
                'arm64' : '',
            }
        self.CC_FLAGS_R.extend( table_arch[ self.getTargetArch() ].split() )

        for inc in self.INCLUDE_PATH_R:
            #print( 'INCLUDE=' + inc )
            self.CC_FLAGS_R.append( '-I' + inc )
        self.CC_FLAGS_R.extend( self.CC_FLAGS )


    def setupLinkFlags( self ):

        self.LINK_FLAGS_R= []
        for lib in self.LIB_PATH_R:
            #print( 'LIB=' + lib )
            self.LINK_FLAGS_R.append( '-LIBPATH:' + lib )
        self.LINK_FLAGS_R.extend( self.LINK_FLAGS )
        for lib in self.LINK_LIBS_R:
            self.LINK_FLAGS_R.append( self.getLibName( lib ) )

    #--------------------------------------------------------------------------

    def getBuildCommand_CC( self, target, src_list ):
        command= []
        command.append( self.CMD_CC )
        command.append( '-c' )
        command.extend( self.CC_FLAGS_R )
        for src in src_list:
            #abs_src= self.tool.host.getGenericPath( src )
            #command.append( abs_src )
            command.append( src )
        command.append( '-Fo' + target )
        return  command

    def getBuildCommand_Link( self, target, src_list ):
        command= []
        command.append( self.CMD_CC )
        command.append( '-Fe' + target )
        for src in src_list:
            command.append( src )
        command.append( '-link' )
        command.extend( self.LINK_FLAGS_R )
        return  command

    def getBuildCommand_Dll( self, target, src_list ):
        command= []
        command.append( self.CMD_CC )
        command.append( '-Fe:' + target )
        for src in src_list:
            command.append( src )
        command.append( '-LD' )
        command.append( '-link' )
        base,ext= os.path.splitext(os.path.basename(target))
        lib_path= self.getLibPath( base )
        command.append( '-IMPLIB:' + lib_path )
        #print( lib_path )
        command.extend( self.LINK_FLAGS_R )
        return  command

    def getBuildCommand_Lib( self, target, src_list ):
        command= []
        command.append( self.CMD_LIB )
        command.append( '-OUT:' + target )
        for src in src_list:
            command.append( src )
        command.extend( self.LIB_FLAGS_R )
        return  command


    def getExeName( self, exe_name ):
        return  exe_name + '.exe'

    def getLibName( self, lib_name ):
        return  lib_name + '.lib'

    def getObjName( self, obj_name ):
        return  obj_name + '.obj'

    def getDllName( self, obj_name ):
        return  obj_name + '.dll'

    #--------------------------------------------------------------------------

    def getSupportArchList( self ):
        #return  [ 'x64', 'x86' ]
        #return  [ 'x64', 'x86', 'arm7', 'arm64' ]
        return  self.ARCH_LIST


