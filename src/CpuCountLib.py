# FlatBuildTool 2019/05/25 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  sys
import  multiprocessing
import  time


class BusyTask:

    def __init__( self ):
        pass

    def busyfunc( self ):
        MAX_LOOP= 5000000
        a= 0
        b= 0
        btime= time.perf_counter()
        for loop in range(MAX_LOOP):
            a+= 1.00382291283 * (loop * 1.00382201039 - 0.0038111)
            b+= a+a
            if (time.perf_counter()-btime) > 0.5:
                break

    def run_busy( self, func ):
        proc_list= []
        cpu_count= os.cpu_count()
        for cpu in range(cpu_count):
            proc= multiprocessing.Process( target=self.busyfunc )
            proc_list.append( proc )
            proc.start()
        time.sleep( 0.2 )
        func()
        for proc in proc_list:
            proc.join()


class CpuInfo:

    def __init__( self ):
        script_bin_path= os.path.dirname( sys.argv[0] )
        self.CACHE_FILE= os.path.join( script_bin_path, '.cpu_count_cache.txt' )
        self.update()

    def update( self ):
        cpu_count= self.load_cache()
        if cpu_count == -1:
            bt= BusyTask()
            bt.run_busy( self.update_list )
            self.save_cache( self.cpu_count )
        else:
            self.cpu_count= cpu_count

    def load_cache( self ):
        if os.path.exists( self.CACHE_FILE ):
            with open( self.CACHE_FILE, 'r', encoding='UTF-8' ) as fi:
                for line in fi:
                    if line[0] == '#':
                        continue
                    params= line.split()
                    if params[0] == 'count':
                        return  int(params[1])
        return  -1

    def save_cache( self, cpu_count ):
        with open( self.CACHE_FILE, 'w', encoding='UTF-8' ) as fo:
            fo.write( 'count %d\n' % cpu_count )

    def update_list( self ):
        self.cpu_count= os.cpu_count()


def getCpuCount():
    if sys.platform == 'win32':
        if 'NUMBER_OF_PROCESSORS' in os.environ:
            return  int(os.environ['NUMBER_OF_PROCESSORS'])
        return  os.cpu_count()
    elif sys.platform == 'linux':
        info= CpuInfo()
        return  info.cpu_count
    return  os.cpu_count()


