# FlatBuildTool

Multi-platform build tool for C/C++

## Supported platform

- Windows x64/x86/arm64/arm
- Linux x86_64/x86/aarch64/armv7l/armv6l
- Android aarch64/armv7a/x86_64/x86
- macOS x86_64

<!--
- iOS arm64/armv7
-->


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


