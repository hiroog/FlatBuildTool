# FlatBuildTool

動的依存解析を行うビルドツールです。スレッド並列化に特化しています。
解析結果をキャッシュしないので、依存が判明した時点で即座に
ビルドを開始することができます。


## 使い方 

```flmake [<options>] [<target_task_name...>]```

target_task_name 何も指定しない場合、デフォルトで "build" Task をビルドします。

|option|詳細|
|:--|:--|
| -f ```<makefile>```  | 読み込む Makefile を指定します。デフォルト "FLB_Makefile.py"  |
| --list     | 定義されているタスク一覧を表示します。   |
| --job ```<n>```  | 並列度を指定します。--job 1 で単一スレッドになります。デフォルトはハードウエアスレッド数。  |
| --opt ```<kname>=<value>```   | 環境変数(ユーザー定義変数)を定義します。   |
| --debug    | 実行 command の echo や Python Error の詳細を表示します。 |


## Makefile

ビルドルールは Makefile に記述します。
デフォルトで、カレントフォルダにある FLB_Makefile.py を読み込みます。
Python 3.x の記法や命令が使えます。

まず Build のために各 Platform の環境を作ります。
この例では Windows 向けにビルドを行うための環境 env が作られます。

```python
env= tool.createTargetEnvironment( 'Windows' )
```

Host と同じ Platform の場合は platform_name を省略できます。
もし Linux 上など 'Windows' 向けの環境を用意できない場合は None を返します。

main.cpp をコンパイルして 'test.exe' を作成するための task を登録します。

```python
tool.addExeTask( env, 'test', [ 'main.cpp' ] )
```

これでビルドできますが、Target をフルパスの exe 名で指定する必要があります。
そのままだと分かりづらいので、task に別名をつけます。

これが最終的な FLB_Makefile.py の内容です。

```python
# FLB_Makefile.py
env= tool.createTargetEnvironment()
task= tool.addExeTask( env, 'test', [ 'main.cpp' ] )
tool.addNamedTask( env, 'build', [task] )
```

flmake コマンドを実行するとビルドできます。
出力は Windows の場合 obj/Windows/x64/Debug/test.exe になります。





## API

### global 変数

下記の変数が最初から定義されています。

| 変数          | 解説                     |
|:--            |:--                       |
| tool          | FlatBuildTool のインスタンス。    |
| genv          | ビルド環境の global 値。createTargetEnvironment() でこの設定値を継承します。  |
| os            | Python3 api (import os)   |
| sys           | Python3 api (import sys)   |
| Log           | FlatBuildTool の Loggin 用 api   |
| BuildUtility  | File 操作などいくつかの API が定義されています。 |

上記以外の Module も import することで利用できます。




### FlatBuildTool API - Platform 環境

#### ```env= tool.createTargetEnvironment( platform_name= genv.getHostPlatform() )```

BuildTarget 用の Local な環境を作成します。親である genv の設定値を引き継ぎます。
PlatformName を指定しない場合は、Build を行っている Host PC の環境と同一であるとみなします。
さらに子の環境を作る場合は env.clone() してください。

例えば Windows 上で実行したら 'Windows'、Linux なら 'Linux' になります。

その Host がサポートしていない Platform の場合は None を返します。

デフォルトでサポートしている Platform

| platform_name   | 対応している Host       | 対応 Architecture      |
|:--              |:--                      |:--                     |
| Windows         | Windows                 | x64, x86, arm64        |
| Linux           | Linux/WSL/Termux/macOS  | x64, x86, arm64, arm7, arm6  |
| macOS           | macOS                   | x64, arm64             |
| Android         | Windows/Linux/macOS     | arm64, arm7, x64, x86, mips64, mips  |

CPU Architecture 名は BuildSystem 内部で統一しています。対応は下記の通り。括弧表記は Platform 内でのサポート終了。

| FlatBuildTool 名   | Windows          | Linux           | macOS/iOS   | Android     |
|:--                 |:--               |:--              |:--          |:--          |
| x64                | x64              | x86_64/AMD64    | x86_64      | x86_64      |
| x86                | x86              | i686            | (i386)      | i686        |
| arm64              | arm64            | aarch64         | arm64       | arm64       |
| arm7               | (arm)            | armv7l/armv7hf  | (armv7)     | armv7-a     |
| arm7s              | --               | --              | armv7s      | --          |
| arm6               | --               | armv6l          | --          | --          |
| (arm5)             | --               | --              | --          | (armv5te)   |
| (mips64)           | --               | --              | --          | (mips64)    |
| (mips)             | --               | --              | --          | (mips)      |


* Linux armv6 = Raspberry Pi
* macOS armv7s = watchOS


#### ```tool.addPlatform( platform_name= HostPlatform )```

新しく Platform を追加します。
自分で Platform を定義する場合に使います。

```python
import PlatformLinuxGCC
tool.addPlatform( 'LinuxGCC', PlatformLinuxGCC )
```

### FlatBuildTool API - Task API

#### ```task= tool.findTask( task_name )```

名前で task を検索します。


#### ```task= tool.addTask( task_name, task_object )```

名前をつけて task を登録します。


#### ```task= tool.removeTask( task_name )```

登録されている task を削除します。



#### ```task= tool.addLibTask( env, task_name, [src_list..] )```

静的 Link ライブラリをビルドするためのタスクを登録します。


#### ```task= tool.addExeTask( env, task_name, [src_list..] )```

実行ファイルをビルドするためのタスクを登録します。


#### ```task= tool.addDllTask( env, task_name, [src_list..] )```

動的 Link ライブラリ/共有ライブラリをビルドするためのタスクを登録します。


#### ```task= tool.addNamedTask( env, task_name, [task_list..] )```

他の Task に別の名前をつけて新しい Task として登録します。
複数の Task をグループ化できますが依存関係はないものとみなします。
可能な限り並列にビルドを行います。


#### ```task= tool.addScriptTask( env, task_name, python_func )```

任意の Python Code を実行します。


#### ```task= tool.addCleanTask( env, task_name )```

生成物を消去するための task を登録します。
この task を実行すると obj ディレクトリを消去します。



### FlatBuildTool API - Script/Submodule API

#### ```tool.execScript( script_name )```

他のファイルを読み込んで実行します。
Makefile の include に相当します。

共通で参照するパラメータや関数などを定義しておくことができます。


#### ```tool.execSubmoduleScripts( script_name, [ submodule_folder... ] )```

別のフォルダにある Makefile を読み込んで task を登録します。
execScript() と違い、task 名を階層化するので同名の task があっても区別できるようになります。


```python
# FLB_Makefile.py
tool.execSubmoduleScripts( 'FLB_Makefile.py', [ 'subfolder1', 'subfolder2' ] )
```

上記の場合 subfolder1/FLB_Makefile.py と subfolder2/FLB_Makefile.py を読み込みます。

それぞれが 'build' task を持っている場合、
'subfolder1/build'、'subfolder2/build' の名前で実行できるようになります。


#### ```task= tool.addSubmoduleTasks( env, task_name, [ submodule_folder... ] )```

階層以下の同名の task をグループ化します。
例えば下記の例では、'subfolder1/build', 'subfolder2/build' の 2つの task をまとめて 'build' というタスク名をつけます。

```python
# FLB_Makefile.py
tool.execSubmoduleScripts( 'FLB_Makefile.py', [ 'subfolder1', 'subfolder2' ] )
tool.addSubmoduleTasks( genv, 'build', [ 'subfolder1', 'subfolder2' ] )
```

これで flmake を呼び出すだけで階層以下の subfolder1/subfolder2 を同時にビルドすることができます。
なお addSubmoduleTasks() でグループ化した task には依存関係がないので注意してください。
可能な限り並列に実行しようとします。


#### ```tool.pushDir( submodule_folder )```

task の namespace に prefix 'submodule_folder/' を追加し、カレントディレクトリを submodule_folder に移します。


#### ```tool.popDir()```

tool.pushDir() に対応します。1 つ前のフォルダに戻ります。


### FlatBuildTool API - その他


#### ```value= tool.findPath( path_name, default_value )```

path_name が存在しているか調べます。存在している場合は path_name をそのまま返します。
存在していない場合は default_value を返します。

```python
# 例
tool.findPath( '../../flatlib5', genv.getEnv( 'FLATLIB5', 'D:/sdk/flatlib5' ) )
```


### FlatBuildTool API - メンバ変数

#### ```tool.global_env```

genv と同じです。 




### Platform Environment API - 共通

#### ```env.clone()```

複製し、ローカルな環境を作成します。
一時的な設定変更を行う場合に使用します。

```python
# 共通の設定
env= tool.createTargetEnvironment()
env.addIncludePaths( [...] )
env.addCCFlags( [...] )
env.addLibraries( [...] )
env.setTargetArch( 'x64' )

debug_env= env.clone()
debug_env.setConfig( 'Debug' )
debug_env.setCCFlags( ['-DLIB_DEBUG_LEVEL=1'] )
debug_env.addLinkPaths( [ os.path.join( debug_lib_path, 'lib' ) ] )
debug_env.refresh()
# debug_env を元にビルドを行う
debug_task= tool.addExeTask( debug_env, 'build_debug', source_lists )

release_env= env.clone()
release_env.setConfig( 'Release' )
release_env.setCCFlags( ['-DLIB_DEBUG_LEVEL=0'] )
release_env.addLinkPaths( [ os.path.join( release_lib_path, 'lib' ) ] )
release_env.refresh()
# release_env を元にビルドを行う
debug_task= tool.addExeTask( release_env, 'build_release', source_lists )
```


#### ```env.refresh()```

環境の内容を更新します。
env.add～ や env.set～ を実行したあとは、最後に呼び出しておいてください。



### Platform Environment API - 検索パス・コマンドライン引数


#### ```env.addIncludePaths( [ path... ] )```

include file の検索パスを追加します。


#### ```env.addLibPaths( [ path... ] )```

library の検索パスを追加します。


#### ```env.addCCFlags( [ option... ] )```

c++ コンパイラに渡す引数を定義します。


#### ```env.addLinkFlags( [ option... ] )```

リンカに渡す引数を定義します。


#### ```env.addLibraries( [ lib... ] )```

リンクするファイルを定義します。
Platform 固有部分は省いてください。

```python
env.addLibraries( [ 'test1', 'test2' ] )

```

* Windows →  "test1.lib test2.lib"
* Windows以外 →  "-ltest1 -ltest2"  (libtest1.a, libtest2.a と同じ)



### Platform Environment API - Config



#### ```env.getHostPlatform()```

ホストの Platform 名を返します。

* 'Windows', 'Linux', 'macOS'


#### ```arch= env.getHostArch()```

ホストの CPU Architecture を返します。

* 'x64', 'x86', 'arm64', 'arm7', 'arm6'


#### ```platform= env.getTargetPlatform()```

ビルド対象の Platform 名を返します。
環境作成時 ( tool.createTargetEnvironment() ) に指定した Platform になります。


#### ```env.setTargetArch( arch_name )```

ビルドを行う CPU Architecture を設定します。


#### ```arch= env.getTargetArch()```

ビルド対象に現在設定されている CPU Architecture を返します。


#### ```env.setConfig( config_name )```

Build Configuration 名を設定します。
デフォルトでは 'Debug', 'Release' の 2種類定義されています。


#### ```config= env.getConfig()```

現在環境に設定されている Build Configuration 名を返します。

* 'Debug', 'Release', 'Retail'


#### ```env.setApiLevel( android_api_level )```

Android Platform のみ有効です。
ビルド対象の API Level を指定します。


#### ```level= env.getApiLevel()```

Android Platform のみ有効です。
現在設定されている API Level を返します。



#### ```arch_list=env.getSupportArchList()```

その Platform がサポートしているアーキテクチャ一覧を返します。

例えば下記のように複数のアーキテクチャのビルドタスクを一度に定義することができます。

```python
task_list= []
for config in [ 'Debug', 'Release' ]:
    for arch in env.getSupportArchList():
        local_env= env.clone()
        local_env.setConfig( config )
        local_env.setTargetArch( arch )
	# Libpath を Config/CPU Architecture 毎に切り替える
        for libpath in libpath_list:
    	    local_env.addLibPaths( [os.path.join( libpath, 'lib', arch, config )] )
        local_env.refresh()
        task= env.tool.addExeTask( local_env, exe_name, src_list )
        task_list.append( task )
# build という task 名でまとめる
task= env.tool.addNamedTask( env, 'build', task_list )
```



### Platform Environment API - Output


#### ```env.setLibDir( lib_dir )```

ライブラリの出力先フォルダを指定します。
ここで指定したフォルダの下に、Platform, Architecture, Config 毎のフォルダが作られます。

#### ```env.setObjDir( lib_dir )```

obj の出力先フォルダを指定します。

#### ```env.setExeDir( lib_dir )```

実行ファイルの出力先フォルダを指定します。
ここで指定したフォルダの下に Platform, Architecture, Config 毎のフォルダが作られます。

出力ファイル名と出力先を完全に制御したい場合は、
ファイル名決定用の関数を定義することができます。
EXE_NAME_FUNC を定義した場合はサブフォルダが作られません。

```
def makeExeName( env, src_name ):
    if src_name:
        return  env.getExeName( src_name + '_' + env.getTargetArch() + '_' + env.getConfig() )
    return  '.'
env.EXE_NAME_FUNC= makeExeName
```


デフォルトの場合

* ./obj/Windows/x64/Release/test.exe
* ./obj/Windows/x64/Debug/test.exe

例の EXE_NAME_FUNC を定義した場合

* ./test_x64_Debug.exe
* ./test_x64_Release.exe



### Platform Environment API - Platform 固有の名前

#### ```file_name= env.getObjName( file_name )```

Platform 固有の obj 名を返します。

* Windows: file_name.obj
* Windows以外: file_name.o

#### ```file_name= env.getExeName( file_name )```

Platform 固有の exe 名を返します。

* Windows: file_name.exe
* Windows以外: file_name

#### ```file_name= env.getLibName( file_name )```

Platform 固有の lib 名を返します。

* Windows: file_name.lib
* Windows以外: libfile_name.a

#### ```file_name= env.getDllName( file_name )```

Platform 固有の dll 名を返します。

* Windows: file_name.dll
* macOS: libfile_name.dylib
* 上記以外: libfile_name.so


### Platform Environment API - User 変数

#### ```value= env.getEnv( name, default_value )```

環境変数(ユーザー定義変数)の値を返します。
変数が定義されていない場合は default_value を返します。

OS で設定した環境変数だけでなく、
コマンドラインオプション --opt や src/local_cconfig.txt で定義した値も読み取ることができます。


#### ```env.setEnv( name, value )```

環境変数(ユーザー定義変数)の値を定義します。
この命令は現在のビルド環境にだけ設定するので、親の環境変数には影響を与えません。



### Platform Environment API - メンバ変数

#### ```env.tool```

FlatBuildTool のインスタンスにアクセスします。



### Task API - メンバ変数

#### ```task.env```

Task を生成したときのビルド環境にアクセスします。




## PC 固有のデフォルトオプション

コンパイラの選択、使用する SIMD 命令の選択など、
ユーザー定義変数を使って PC 固有のデフォルトオプションを設定しておくことができます。

例えば Windows の場合、どの VisualStudio を使うのか選択できます。

```
VC 2017
```

Visual Studio 2017/2019 両方インストールしている場合デフォルトでは 2019 を使いますが、
上記の内容を FlatBuildTool/src/local_cconfig.txt の名前で保存しておくと VisualStudio 2017 を選択します。

設定できる値は FlatBuildTool/src/local_cconfig.sample.txt を参照してください。

local_cconfig.txt だけでなくコマンドラインから指定することもできます。

```
$ flmake --opt VC=2017
```

Makefile 内で定義する場合は env.setEnv() を使用します。


```python
genv.setEnv( 'VC', '2017' )
```



