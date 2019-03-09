# FlatBuildTool 2017/07/24 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:


def compile( task ):

    if task.env.getHostPlatform() == 'Windows':
        PYZ_FILE= 'flmake.pyz'
    else:
        PYZ_FILE= '../bin/flmake.pyz'
    TEMP_DIR= 'obj'
    MAIN_FILE= 'flmain.exe'
    EXE_FILE= '../bin/flmake.exe'
    if not os.path.exists( '../bin' ):
        os.mkdir( '../bin' )

    ### pyc compile
    if not os.path.exists( TEMP_DIR ):
        os.mkdir( TEMP_DIR )
    src_list= [
            'FlatBuildTool.py',
            'BuildUtility.py',
            'Depend.py',
            'JobQueue.py',
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
    import  zipapp
    zipapp.create_archive( TEMP_DIR, PYZ_FILE, '/usr/bin/env python3', 'FlatBuildTool:main' )
    os.chmod( PYZ_FILE, 0o755 )

    if task.env.getHostPlatform() == 'Windows':

        ### exe compile
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
        with open( EXE_FILE, 'wb' ) as fo:
            with open( MAIN_FILE, 'rb' ) as fi:
                fo.write( fi.read() )
            with open( PYZ_FILE, 'rb' ) as fi:
                fo.write( fi.read() )

        ### copy
        copy_list= [
                'FLB_Default.py',
                'flmake.exe',
            ]
    else:
        ### copy
        copy_list= [
                'FLB_Default.py',
            ]
    BuildUtility.CopyFilesDir( copy_list, '../bin' )



tool.addScriptTask( genv, 'compile', compile )



def usage( task ):
    print( 'usage: flmake compile' )

tool.addScriptTask( genv, 'build', usage )


