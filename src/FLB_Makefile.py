# FlatBuildTool 2017/07/24 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:


def compile( task ):
    ### pyc compile
    TEMP_DIR= 'obj'
    if not os.path.exists( TEMP_DIR ):
        os.mkdir( TEMP_DIR )
    src_list= [
            'FlatBuildTool.py',
            'BuildUtility.py',
            'Depend.py',
            'JobQueue.py',
            'CpuCountLib.py',
            'PlatformCommon.py',
            'PlatformAndroid.py',
            'PlatformLinux.py',
            'PlatformMacOS.py',
            'PlatformWindows.py',
            'PlatformIOS.py',
            'PlatformCS.py',
            'PlatformMetal.py',
        ]
    import  py_compile
    for src in src_list:
        py_compile.compile( src, cfile= TEMP_DIR + '/' + src + 'c' )

    ### pyz build
    FLMAKE_PYZ= 'flmake.pyz'
    import  zipapp
    zipapp.create_archive( TEMP_DIR, FLMAKE_PYZ, '/usr/bin/env python3', 'FlatBuildTool:main' )
    os.chmod( FLMAKE_PYZ, 0o755 )

    if task.env.getHostPlatform() == 'Windows':

        ### exe compile
        MAIN_EXE= 'flmain.exe'
        FLMAKE_EXE= 'flmake.exe'
        if not os.path.exists( MAIN_EXE ):
            csrc_code= 'flmain.c'
            from distutils.ccompiler import new_compiler
            import distutils.sysconfig
            from pathlib import Path
            src= Path( csrc_code )
            cc= new_compiler()
            exe= src.stem
            cc.add_include_dir( distutils.sysconfig.get_python_inc() )
            cc.add_library_dir( os.path.join( sys.base_exec_prefix, 'libs' ) )
            objs= cc.compile( [ str(src) ] )
            cc.link_executable( objs, exe )

        ### append
        with open( FLMAKE_EXE, 'wb' ) as fo:
            with open( MAIN_EXE, 'rb' ) as fi:
                fo.write( fi.read() )
            with open( FLMAKE_PYZ, 'rb' ) as fi:
                fo.write( fi.read() )

        ### copy
        copy_list= [
                'FLB_Default.py',
                'flmake.exe',
                'local_config.sample.txt',
            ]
    else:
        ### copy
        copy_list= [
                'FLB_Default.py',
                'flmake.pyz',
                'local_config.sample.txt',
                'local_config.termux.txt',
            ]
    ### install
    INSTALL_DIR= '../bin'
    BuildUtility.CopyFilesDir( copy_list, INSTALL_DIR )



tool.addScriptTask( genv, 'compile', compile )



def usage( task ):
    print( 'usage: flmake compile' )

tool.addScriptTask( genv, 'build', usage )


