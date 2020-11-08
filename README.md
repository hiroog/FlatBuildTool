# FlatBuildTool

Multi-platform build tool for C/C++

## Supported platform

- Windows x86/x64
- Linux x86/x64/armv6/armv7/arm64
- Android armv7/arm64/x86/x64
- macOS x64
- iOS armv7/arm64


## How to use

### Makefile

```python
# FLB_Makefile.py
env= tool.createTargetEnvironment()
task= tool.addExeTask( env, 'test', [ 'main.cpp' ] )
tool.addTask( 'build', task )
```

### Build

```
$ flmake
```






