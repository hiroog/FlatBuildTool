# sample makefile
# vim:ts=4 sw=4 et:

env= tool.createTargetEnvironment()


task= tool.addExeTask( env, 'test', [ 'test.cpp' ] )
tool.addNamedTask( env, 'all', [task] )

#tool.addJob( task )



def clean_task( task ):
    Log.p( 'CLEAN' )
    import shutil
    shutil.rmtree( task.env.OUTPUT_OBJ_DIR )

tool.addScriptTask( env, 'clean', clean_task )

tool.addNamedTask( env, 'build', [task] )


