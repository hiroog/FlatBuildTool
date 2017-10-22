# test makefile


def dumpEnvironment( env, config, arch ):

    def dumpFlags( env, attr_name ):
        data= getattr( env, attr_name, None )
        if data != None:
            print( attr_name + ' = ' )
            for flag in data:
                print( '  ' + flag )
        print()

    def dumpCommandLine( msg, command ):
        print( msg + ' ' + ' '.join( command ) )


    env.summary()

    env.setConfig( config )
    env.setTargetArch( arch )
    env.refresh()

    print()

    print( 'CMD_CC   = ' + env.CMD_CC )
    print( 'CMD_LINK = ' + env.CMD_LINK )
    print( 'CMD_LIB  = ' + env.CMD_LIB )

    print()

    print( 'getObjPath = ' + env.getObjPath( 'test' ) )
    print( 'getExePath = ' + env.getExePath( 'test' ) )
    print( 'getLibPath = ' + env.getLibPath( 'test' ) )
    print()
    print( 'getObjName = ' + env.getObjName( 'test' ) )
    print( 'getExeName = ' + env.getExeName( 'test' ) )
    print( 'getLibName = ' + env.getLibName( 'test' ) )

    print()

    dumpFlags( env, 'INCLUDE_PATH_R' )
    dumpFlags( env, 'LIB_PATH_R' )
    dumpFlags( env, 'BIN_PATH_R' )

    print()

    dumpFlags( env, 'CC_FLAGS_R'  )
    dumpFlags( env, 'LINK_FLAGS_R' )
    dumpFlags( env, 'LIB_FLAGS_R' )

    print()

    obj_name= env.getObjPath( 'test' )
    dumpCommandLine( 'cc', env.getBuildCommand_CC( obj_name, [ "test.cpp" ] ) )
    print()
    dumpCommandLine( 'ld', env.getBuildCommand_Link( env.getExePath( 'test' ), [ obj_name ] ) )
    print()
    dumpCommandLine( 'ar', env.getBuildCommand_Lib( env.getLibPath( 'test' ), [ obj_name ] ) )





env= tool.createTargetEnvironment( genv.getHostPlatform() )
#env= tool.createTargetEnvironment( 'Android' )
#dumpEnvironment( env, 'Debug', 'arm7' )
dumpEnvironment( env, 'Debug', 'x64' )




tool.addNamedTask( env, 'build', [] )

