# FlatBuildTool 2017/07/22 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  threading
import  multiprocessing
import  BuildUtility

from collections import deque
from BuildUtility import Log


#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

class JobQueue:

    def __init__( self ):
        self.queue= deque()
        self.lock= threading.Lock()
        self.result_code= 0

    def pushJob( self, job ):
        with self.lock:
            self.queue.append( job )

    def setBreak( self, code ):
        with self.lock:
            self.result_code= code

    def isBreak( self ):
        return  self.result_code != 0

    def getResultCode( self ):
        return  self.result_code

    def popJob( self ):
        with self.lock:
            if len( self.queue ) == 0:
                return  None
            return  self.queue.popleft()

    def dumpQueue( self ):
        Log.p( 'JobQueue:' )
        with self.lock:
            for job in self.queue:
                Log.p( str(job) )




class WorkerThread( threading.Thread ):

    def __init__( self, index, queue ):
        super().__init__()
        self.index= index
        self.queue= queue

    def run( self ):
        while True:
            if self.queue.isBreak():
                Log.d( 'Quit thread %d' % self.index )
                break
            job= self.queue.popJob()
            if job == None:
                Log.d( 'End thread %d' % self.index )
                break
            #print( ' Run %d' % self.index )
            try:
                code= job.run()
            except BuildUtility.FLB_Error as err:
                Log.e( err )
                code= 100
            except:
                Log.e( 'Exception! in thread %d' % self.index )
                raise
            if code != 0:
                self.queue.setBreak( code )
                break
        #print( 'thread end %d' % self.index )




class ThreadPool:

    def __init__( self, max_thread ):
        self.job_queue= JobQueue()
        self.lock= threading.Lock()
        self.max_thread= max_thread
        if max_thread == 0:
            self.max_thread= multiprocessing.cpu_count()
        self.thread_list= []
        Log.d( 'Thread = %d' % self.max_thread )

    def addThread( self ):
        if len( self.thread_list ) < self.max_thread:
            index= 0
            with self.lock:
                index= len(self.thread_list)
                thread= WorkerThread( index, self.job_queue )
                self.thread_list.append( thread )
            Log.d( 'Start thread %d' % index )
            thread.start()

    def join( self ):
        for thread in self.thread_list:
            thread.join()
        with self.lock:
            self.thread_list= []

    def addJob( self, job ):
        if job == None:
            raise  BuildUtility.FLB_Error( 'Null Job' )
        self.job_queue.pushJob( job )
        self.addThread()



#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

