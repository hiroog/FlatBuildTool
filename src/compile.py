# FlatBuildTool 2017/07/23 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

from distutils.core import setup
import  py2exe


output_dir= "../bin"

opt= {
        "compressed" : True,
        "optimize" : 2,
        "bundle_files" : 3,
        "includes" : [
                "Depend",
                "JobQueue",
                "BuildUtility",
                "BRCCNetLib",
                "PlatformCommon",
                "PlatformWindows",
                "PlatformLinux",
                "PlatformAndroid",
                "PlatformCS",
                "PlatformMacOS",
            ],
        "dist_dir" : output_dir,
    }


setup(
    options = { "py2exe" : opt },
    console = [ 'FlatBuildTool.py' ]
    )



