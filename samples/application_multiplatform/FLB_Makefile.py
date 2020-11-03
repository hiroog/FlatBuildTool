# build all architectures and configuration

src_list= [
    'function.cpp',
]

platform_list= [
        #'Windows',
        genv.getHostPlatform(),
        'Android',
    ]

config_list= [
        'Debug',
        'Release',
    ]


LIB_NAME= 'test'
task_list= []



for platform in platform_list:

    env= tool.createTargetEnvironment( platform )
    if not env.isValid():
        continue
    env.setApiLevel( 24 )

    for target_arch in env.getSupportArchList():

        env.setTargetArch( target_arch )

        for config in config_list:

            env.setConfig( config )
            env.refresh()
            task_list.append( tool.addLibTask( env, LIB_NAME, src_list ) )



tool.addNamedTask( genv, 'build', task_list )



