# FlatBuildTool 2017/07/24 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

def compile( task ):
    BuildUtility.ExecCommand( [ 'python', 'compile.py', 'py2exe' ] )
    copy_list= [
            'FLB_Default.py'
        ]
    BuildUtility.CopyFilesDir( copy_list, '../bin' )


tool.addScriptTask( genv, 'compile', compile )


def message( task ):
    print( 'usage: flmake compile' )


tool.addScriptTask( genv, 'build', message )

