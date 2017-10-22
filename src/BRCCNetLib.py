# 2017/07/27 Hiroyuki Ogasawara
# vim:ts=4 sw=4 et:

import  os
import  re
import  socket
import  multiprocessing


class BRCC_Error( Exception ):
    def __init__( self, message ):
        self.message= message
    def __str__( self ):
        return  self.message


class CommandHeader:

    def __init__( self, command= '', binary= None ):
        self.size= 0
        self.command= command
        self.binary= binary
        self.arg_list= []
        self.option= {}

    def isValidData( self ):
        return  self.size == len(self.binary)

    def setOpt( self, name, param ):
        self.option[ name ]= param
        return  self

    def setArg( self, arg_list ):
        self.arg_list= arg_list[:]

    def addArg( self, param ):
        self.arg_list.append( param )
        return  self

    def getOpt( self, name ):
        if name in self.option:
            return  self.option[ name ]
        return  None





class ConnectionSocket:

    cmd_pat= re.compile( r'^([a-zA-Z0-9_]+)\s+(.*)$' )

    def __init__( self, sock, addr ):
        self.addr= addr
        self.sock= sock
        self.BUFFER_SIZE= 1024 * 1024 * 2

    @staticmethod
    def createFromHost( host, port, ip_version= 4 ):
        family,addr= ConnectionSocket.getAddr( host, port, ip_version )
        sock= socket.socket( family, socket.SOCK_STREAM )
        return  ConnectionSocket( sock, addr )

    def __enter__( self ):
        return  self

    def __exit__( self, exception_type, exception_value, traceback ):
        self.close()
        return  True


    @staticmethod
    def getAddr( host, port, ip_version= 4 ):
        if ip_version == 4:
            filter_family= socket.AF_INET
        else:
            filter_family= socket.AF_INET6
        for family,type,proto,ca,addr in socket.getaddrinfo( host, port, proto=socket.IPPROTO_TCP, family=filter_family ):
        #for family,type,proto,ca,addr in socket.getaddrinfo( host, port, proto=socket.IPPROTO_TCP ):
            #print( ' family=' + str(family) )
            #print( ' type=' + str(type) )
            #print( ' proto=' + str(proto) )
            #print( ' ca=' + str(ca) )
            #print( ' addr=' + str(addr) )
            return  family,addr
        return  None,None


    def connect( self ):
        self.sock.connect( self.addr )


    def parse_header( self, header_text ):
        header= CommandHeader()
        for line in header_text.split( '\n' ):
            pat= self.cmd_pat.search( line )
            if pat:
                cmd= pat.group( 1 )
                arg= pat.group( 2 )
                #Log.d( '  - parse "%s" "%s"' % (cmd,arg) )
                if cmd == 'size':
                    header.size= int(arg)
                elif cmd == 'cmd':
                    header.command= arg
                elif cmd == 'a':
                    header.addArg( arg )
                else:
                    header.option[cmd]= arg
        return  header


    def recvData( self ):
        header= None
        try:
            data_buffer= b''
            while True:
                read_buffer= self.sock.recv( self.BUFFER_SIZE )
                if len(read_buffer) == 0:
                    return  None
                data_buffer+= read_buffer
                position= data_buffer.find( b'\nend\n' )
                if position >= 0:
                    #Log.d( 'RecvCmd %d byte' % len(data_buffer) )
                    break

            header_binary= data_buffer[:position]
            header_text= header_binary.decode( encoding='utf-8' )
            #Log.d( 'header text=[%s]' % header_text )
            header= self.parse_header( header_text )
            data_binary= data_buffer[position+5:]
            #Log.d( '  bin  %d' % len(data_binary) )
            while len(data_binary) < header.size:
                data_buffer= self.sock.recv( self.BUFFER_SIZE )
                if len(data_buffer) == 0:
                    return  None
                #Log.d( '  recv %d' % len(data_buffer) )
                data_binary+= data_buffer
            header.binary= data_binary

        except ConnectionResetError:
            #Log.e( 'recvData ConnectionResetError!!' )
            print( 'Error: recvData ConnectionResetError!!' )
            return  None
        except:
            raise
        return  header


    def sendBinary( self, binary ):
        data_size= len(binary)
        #Log.d( 'SendCmd %d byte' % data_size )
        sent_size= 0
        while sent_size < data_size:
            size= self.sock.send( binary[sent_size:] )
            #Log.d( '  sent %d' % size )
            if size == 0:
                raise   BRCC_Error( 'socket closed' )
            sent_size+= size


    def sendData( self, header ):
        header_text= 'cmd %s\n' % header.command
        for arg in header.arg_list:
            header_text+= 'a %s\n' % arg
        if header.binary:
            header_text+= 'size %d\n' % len(header.binary)
        for opt in header.option:
            header_text+= '%s %s\n' % (opt,header.option[opt])
        header_text+= 'end\n'
        header_binary= header_text.encode( 'utf-8' )
        #print( 'sendData=' + header_text )
        #print( 'bin=' + header.binary )
        if header.binary:
            self.sendBinary( header_binary + header.binary )
        else:
            self.sendBinary( header_binary )


    def close( self ):
        if self.sock:
            #self.sock.shutdown( 0 )
            self.sock.close()
            self.sock= None



#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

def GetBRCCRoot():
    if 'BRCC_ROOT' in os.environ:
        return  os.environ[ 'BRCC_ROOT' ]
    if 'DUBA_LOCAL_ROOT' in os.environ:
        return  os.path.join( os.environ[ 'DUBA_LOCAL_ROOT' ], 'tools/brcc' )
    brcc_path= os.path.dirname( os.path.dirname( sys.argv[0] ) )
    return  brcc_path


class ClientConfig:

    CACHE_DIR= 'cache'

    def __init__( self, load= True ):
        self.BRCC_ROOT= GetBRCCRoot()
        self.lock_host= None
        self.lock_port= 19980
        self.build_host= '0.0.0.0'
        self.build_port= 19800
        self.remote_thread= 200
        self.local_thread= multiprocessing.cpu_count()
        self.client_cache= False
        self.server_cache= True
        self.debug= False
        self.enable= True
        self.python= None
        self.cache_dir= os.path.join( self.BRCC_ROOT, ClientConfig.CACHE_DIR )
        self.cache_engine= None
        if load:
            self.loadConfig()

    def isAvailable( self ):
        return  self.lock_host is not None

    def loadConfig( self ):
        with open( os.path.join( self.BRCC_ROOT, 'ClientConfig.txt' ), 'r' ) as fi:
            for line in fi:
                if line == '' or line[0] == '#':
                    continue
                line= line.strip( ' \t\n' )
                if line.startswith( 'server' ):
                    params= line.split()
                    self.lock_host= params[1]
                    self.lock_port= int(params[2])
                elif line.startswith( 'thread' ):
                    params= line.split()
                    self.remote_thread= int(params[1])
                elif line.startswith( 'build' ):
                    params= line.split()
                    self.build_host= params[1]
                    self.build_port= int(params[2])
                elif line.startswith( 'local' ):
                    params= line.split()
                    self.local_thread= int(params[1])
                elif line.startswith( 'cache' ):
                    params= line.split()
                    self.cache_dir= params[1]
                elif line.startswith( 'cscache' ):
                    params= line.split()
                    self.client_cache= int(params[1]) != 0
                elif line.startswith( 'sscache' ):
                    params= line.split()
                    self.server_cache= int(params[1]) != 0
                elif line.startswith( 'debug' ):
                    params= line.split()
                    self.debug= int(params[1]) != 0
                elif line.startswith( 'enable' ):
                    params= line.split()
                    self.enable= int(params[1]) != 0
                elif line.startswith( 'python' ):
                    params= line.split()
                    self.python= params[1]


    def getRemoteThreadCount( self ):
        remote_thread= self.local_thread
        with ConnectionSocket.createFromHost( self.lock_host, self.lock_port ) as connection:
            connection.connect()
            connection.sendData( CommandHeader( 'th' ) )
            header= connection.recvData()
            remote_thread= int( header.getOpt( 'th' ) )
            if remote_thread > self.remote_thread:
                remote_thread= self.remote_thread
        return  remote_thread



#------------------------------------------------------------------------------
#------------------------------------------------------------------------------

