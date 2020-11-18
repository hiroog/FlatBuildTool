# FlatBuildTool

動的依存解析を行うビルドツールです。
スレッド並列化に特化しており、可能な限り並列にビルドを行います。
依存解析とビルドも並列に行われます。
解析結果をキャッシュしないので、依存が判明した時点で即座に
ビルドを開始することができます。

ソースコード数が少なくても、Debug と Release、x64 と x86 などの複数のターゲットを
並列にビルドすることができます。
ソースコード間で依存解析結果を共有するため、一度にビルドする対象が増えれば増えるほど効率が上がります。

Python で書かれており、Makefile 自体も Python コードをそのまま使います。
大変自由度が高くなっています。



## 使い方

Python 3.x が必要です。

```flmake [<options>] [<target_task_name...>]```

target_task_name 何も指定しない場合、デフォルトで "build" Task を実行します。

|option|詳細|
|:--|:--|
| -f ```<makefile>```  | 読み込む Makefile を指定します。デフォルト "FLB_Makefile.py"  |
| --list     | 定義されているタスク一覧を表示します。   |
| --job ```<n>```  | 並列度を指定します。--job 1 で単一スレッドになります。デフォルトはハードウエアスレッド数。  |
| --opt ```<kname>=<value>```   | 環境変数(ユーザー定義変数)を定義します。   |
| --verbose  | Build 中の表示を増やします。 |
| --debug    | 実行 command の echo や Python Error の詳細を表示します。 |


target を複数与えた場合、Dependency Graph に従い可能な限り並列にビルドが行われます。
下記の例では build_release と buld_debug が並列に走ります。

```
$ flmake build_release build_debug
```

もし clean と build のように明確な順序付けが必要な場合は、スペースではなくカンマ区切りで与えてください。
この場合 clean が完了してから build が走るようになります。

```
$ flmake clean,build
```




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
tool.addTask( 'build', task )  # alias
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

#### ```env= tool.createTargetEnvironment( platform= None, env= None )```

BuildTarget 用の Local な環境を作成します。親である genv の設定値を引き継ぎます。
PlatformName を指定しない場合は、Build を行っている Host PC の環境と同一であるとみなします。
さらに子の環境を作る場合は env.clone() してください。

例えば Windows 上で実行したら 'Windows'、Linux なら 'Linux' になります。

その Host がサポートしていない Platform の場合は None を返します。

デフォルトでサポートしている Platform

| platform        | 対応している Host       | 対応 Architecture      |
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

名前で Task を検索します。


#### ```task= tool.addTask( task_name, task )```

名前をつけて task を登録します。
既存の Task に別名をつけることもできます。


#### ```task= tool.removeTask( task_name )```

登録されている task を削除します。



#### ```task= tool.addLibTask( env, name, src_list, task_list= None, target= None )```

Static Link ライブラリをビルドするためのタスクを登録します。
依存する Task がある場合 task_list を与えることができます。task_list は省略できます。


#### ```task= tool.addExeTask( env, name, src_list, task_list= None, target= None )```

実行ファイルを生成するためのタスクを登録します。
依存する Task がある場合 task_list を与えることができます。task_list は省略できます。

name の代わりに target を使うと、出力ファイル名を直接指定することができます。
name を使う場合は obj/PLATFORM/ARCH/CONFIG/name.exe に作られます。

```python
tool.addExeTask( env, 'test', [ 'main.cpp' ] )
# --> ./obj/Windows/x64/Debug/test.exe
```

```python
tool.addExeTask( env, src_list= [ 'main.cpp' ], target= 'test_' + env.getConfig() )
# --> ./test_Debug.exe
```

出力ファイル名のフルパスがそのまま Task 名になります。


#### ```task= tool.addDllTask( env, name, src_list, task_list= None, target= None )```

動的 Link ライブラリ/共有ライブラリをビルドするためのタスクを登録します。
依存する Task がある場合 task_list を与えることができます。task_list は省略できます。


#### ```task= tool.addGroupTask( env, task_name, task_list )```

複数の Task をグループ化して新しい Task として登録します。
登録した Task 同士には依存関係はないものとみなし、可能な限り並列に実行を行います。

```python
tool.addGroupTask( genv, 'build', [task1, task2] )
```


#### ```task= tool.addScriptTask( env, task_name, script, task_list= None )```

任意の Python 関数 script を実行します。
python_func には引数として自分自身の task が渡ります。

関数にパラメータを渡したい場合は task Object に追加してください。

```python
def print_func( task ):
    print( task.message )

task= tool.addScriptTask( genv, 'build', print_func )
task.message= 'print message'
```

task_list は省略可能です。
task_list が与えられた場合は task_list の完了を待ってから script を実行します。
script が None の場合 addGroupTask() と同等になります。

```python
tool.addScriptTask( genv, 'build', None, [task1, task2] )
```


#### ```task= tool.addCleanTask( env, task_name, task_list= None )```

生成物を消去するための task を登録します。
この Task を実行すると obj ディレクトリを消去します。



### FlatBuildTool API - Script/Submodule API

#### ```tool.execScript( script_name )```

他のファイルを読み込んで実行します。
Makefile の include に相当します。

共通で参照するパラメータや関数などを定義しておくことができます。


#### ```tool.execSubmoduleScripts( file_name, module_list )```

別のフォルダにある Makefile を読み込んで task を登録します。
execScript() と違い、task 名を階層化するので同名の task があっても区別できるようになります。


```python
# FLB_Makefile.py
tool.execSubmoduleScripts( 'FLB_Makefile.py', [ 'subfolder1', 'subfolder2' ] )
```

上記の場合 subfolder1/FLB_Makefile.py と subfolder2/FLB_Makefile.py を読み込みます。

それぞれが 'build' task を持っている場合、
'subfolder1/build'、'subfolder2/build' の名前で実行できるようになります。


#### ```task= tool.addSubmoduleTasks( env, task_name, module_list, target_name= None, task_list= None )```

階層以下の同名の task をグループ化します。
target_name を省略した場合は task_name と同じものとみなします。

例えば下記の例では、'subfolder1/build', 'subfolder2/build' の 2つの task をまとめて 'build' というタスク名をつけます。


```python
# FLB_Makefile.py
tool.execSubmoduleScripts( 'FLB_Makefile.py', [ 'subfolder1', 'subfolder2' ] )
tool.addSubmoduleTasks( genv, 'build', [ 'subfolder1', 'subfolder2' ] )
```

これで flmake を呼び出すだけで階層以下の subfolder1/subfolder2 を同時にビルドすることができます。
なお addSubmoduleTasks() でグループ化した task には依存関係がないので注意してください。
可能な限り並列に実行しようとします。


#### ```tool.pushDir( dir, prefix= None )```

Task の namespace に prefix を追加し、サブディレクトリ dir に移動します。
prefix を省略すると dir と同じ名前になります。


#### ```tool.popDir()```

tool.pushDir() に対応します。1 つ前のフォルダに戻ります。


### FlatBuildTool API - その他


#### ```value= tool.findPath( path, env_name )```

path が存在しているか調べます。存在している場合は path をフルパスに変換して返します。
存在していない場合は環境変数 path の値を調べて、パスが存在していればその値を返します。
見つからない場合は None を返します。

```python
# 例
tool.findPath( '../../flatlib5', 'FLATLIB5' )
```


#### ```tool.f_list()```

Task 一覧を表示します。
flmake --list と同じです。


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
        task= tool.addExeTask( local_env, exe_name, src_list )
        task_list.append( task )
# build という task 名でグループ化する
task= tool.addGroupTask( env, 'build', task_list )
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


#### ```env.getOutputPath( path )```

getTargetPlatform(), getTargetArch(), getConfig() をつなげたパスを返します。
例えば env.getOutputPath( 'lib' ) の場合「lib/Windows/x64/Debug」をフルパスで返します。


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


### Platform Environment API - その他

#### ```env.isValid()```

Platform 環境が有効かどうか調べます。
SDK が Install されていない場合は False を返します。

```python
env= tool.createTargetEnvironment( 'Android' )
if env.isValid():
    sdk installed
```



### Platform Environment API - メンバ変数

#### ```env.tool```

FlatBuildTool のインスタンスにアクセスします。


### Task API - Dependency Graph

#### ```task.addDependTasks( [task..] )```

依存タスクを追加します。

#### ```task.onCompleteTask( task )```

完了時に走る Task を追加登録します。
同期バリアの挿入に相当します。


### Task API - メンバ変数

#### ```task.env```

Task を生成したときのビルド環境にアクセスします。


### Log API

#### ```Log.p( text )```

Console に表示出力します。

#### ```Log.v( text )```

--verbose (-v) オプション指定時に表示出力します。

#### ```Log.d( text )```

Console に表示出力します。

--debug オプション指定時に表示出力します。

#### ```Log.e( text )```

Console に Error 出力します。



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



## Build Graph

FL_Makefile.py に記述する Python code は Build Graph の構築を行っています。
各 Task は明確な依存が存在しない限り並列に実行しようとします。

例えば下記のように Task A が A1, A2 に依存している場合、A1, A2 両方が完了してから A をビルドします。

```
A1   A2
|     |
+--+--+
   |
   v
   A
```

このとき A1, A2 の間には依存がないので、A1, A2 は同時にビルドが行われます。

同じように B1, B2 に依存する Task B が存在しているものとします。

```
A1   A2   B1   B2
|     |   |     |
+--+--+   +--+--+
   |         |
   v         v
   A         B
```

B のビルドに A が必要な場合、下記のように依存を追加することができます。

```
A1   A2
|     |
+--+--+
   |
   v
   A   B1  B2
   |   |   |
   +---+---+
       |
       v
       B
```

B のビルド全体が、A のビルドが完全に終わるのを待っているわけではない点に注意してください。

A のビルドそのものは B よりも前に行われますが、
A, B1, B2 自体は並列にビルドが行われます。
つまり A1, A2, B1, B2 そのものは同時にビルドが走る可能性があります。


特に Group 化や Submodule などで Task の依存階層が深くなっていると、この仕組が問題になることがあります。
例えば下記のように static library lib1, lib2 のビルドを待ってから application app のビルドを行いたい場合を考えます。

```python
lib_task1= tool.addLibTask( env, 'lib1', src_list_lib1 )
lib_task2= tool.addLibTask( env, 'lib2', src_list_lib2 )
lib_task= tool.addGroupTask( env, 'build_lib', [lib_task1, lib_task2] )

app_task= tool.addExeTask( env, 'app', src_list_app )
tool.addGroupTask( env, 'build_app', [app_task], [lib_task] ) # <== 依存
```

上のグラフは下記のようになります。S0～S5 はソースコードのコンパイルです。

```
S0    S1  S2    S3     S4    S5
|     |   |     |      |     |
+--+--+   +--+--+      +--+--+
   |         |            |
  lib1      lib2         app(link)
   |         |            |
   +----+----+            |
        |                 |
    build_lib             |
        |                 |
        +--------+--------+
             build_app
```

build_app は build_lib に依存していますが、build_lib と app は同時にビルドが行われるため、
結局全てのビルドが並列に走ることになります。
つまり lib1, lib2 のビルドが終わる前に app の link が走る可能性があります。

正しくは build_app ではなく app (link) が build_lib に依存しているからです。

下記のように app の Link 部分に build_lib の依存を接続すれば意図したとおりになります。

```python
lib_task1= tool.addLibTask( env, 'lib1', src_list_lib1 )
lib_task2= tool.addLibTask( env, 'lib2', src_list_lib2 )
lib_task= tool.addGroupTask( env, 'build_lib', [lib_task1, lib_task2] )

app_task= tool.addExeTask( env, 'app', src_list_app, [lib_task] ) # <== 依存
tool.addGroupTask( env, 'build_app', [app_task] )
```

```
S0    S1  S2    S3
|     |   |     |
+--+--+   +--+--+
   |         |
  lib1      lib2
   |         |
   +----+----+
        |
     build_lib      S4    S5
        |           |     |
        +--------+--+-----+
                 |
                app(link)
                 |
              build_app
```
これで lib1, lib2 及び S4, S5 のコンパイルが終わってから app の Link が走るようになります。

ただし Group 化や Submodule などで Task の依存階層が深くなると、途中に依存 Task を挿入するのが難しくなります。

どうしても明確な完了待ち必要になった場合は、依存 Task ではなく完了 Task を追加することで順序付けすることができます。
完了タスクは下記のように同期バリアが挿入されます。

```python
lib_task1= tool.addLibTask( env, 'lib1', src_list_lib1 )
lib_task2= tool.addLibTask( env, 'lib2', src_list_lib2 )
lib_task= tool.addGroupTask( env, 'build_lib', [lib_task1, lib_task2] )

app_task= tool.addExeTask( env, 'app', src_list_app )
lib_task.onCompleteTask( app_task )  # <== 完了タスク

tool.addGroupTask( env, 'build_app', [lib_task] ) # <== 呼び出すのは lib の方
```

```
S0    S1  S2    S3
|     |   |     |
+--+--+   +--+--+
   |         |
  lib1      lib2
   |         |
   +----+----+
        |
     build_lib
        |
  ============================== barrier
        |           S4    S5
        |           |     |
        |           +--+--+
        |              |
        |          progapp(link)
        |              |
        +------->  build_app
```

ただしこの方法では、本来同時にビルドできるはずの S0～S3 と S4, S5 が同時にビルドが行われません。
S0～S3 と lib1/lib2 のビルドを待ってから S4, S5 のコンパイルも走るので並列度が下がります。
簡単に順序付けできる反面、ビルド効率が落ちるので注意してください。
効率を優先する場合は正しい Dependency Graph を作成することをおすすめします。

* sampels/application_and_staticlib は submodule を使いつつ最小限の依存を定義しています。
* sampels/application_and_dynamiclib は file copy に完了タスクを使っています。



## 組み込み版の作成

1. FlatBuildTool/bin に embedded 版 python を展開しておきます。
2. FlatBuildTool/src の中で python ./FlatBuildTool.py compile を実行します。


## Thread Count

Windows 以外の環境では、初回起動時に取得したハードウエア Thread 数を FlatBuildTool/src/.cpu_count_cache.txt ファイルにキャッシュします。
一部の ARM Processor では一定の負荷をかけないと正しい値が取れないためです。
スレッド数が正しくない場合は .cpu_count_cache.txt を削除してみてください。


## Bug

* 依存解析の早期打ち切りのため、メモリキャッシュ化されている依存ファイルの最終更新時間が必ずしも正確にならない可能性があります。
* 動的解析のため、プロジェクト規模が大きい場合効率が落ちる可能性があります。

