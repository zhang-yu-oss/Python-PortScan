import socket
import threading
import re
import sys
import queue
from optparse import OptionParser
RED= '\033[1;31m'
GREE= '\033[1;32m'
Yllo= '\033[1;33m'
que=queue.Queue()     #声明一个对象
USAGE='''
usage:python duankou.py 8.8.8.8
      python duankou.py 8.8.8.8 -p 21,80,8080
      python duankou.py 8.8.8.8 -p 21,80,8080 -n 50
'''
class Scanner(object):   #定义一个类
    def __init__(self,target,port,threadnum = 100):#self只有在类的方法中才会有，独立的函数或方法是不必带有self的
        #正则匹配IP地址是否符合IPV4的格式
        self.target=target 
        self.port=port
        self.threadnum=threadnum
    def start(self):
        if self.port == 65535:  
            for i in range(0,65537):
                que.put(i) #向队列（第三方）中发送端口，队列中数据，先进先出
        else:
            for i in self.port:
                if int(i) < 0 or int(i)>65535:
                    print(RED + '\n[-] 端口错误！请指定0~65535的端口')
                    exit()
                que.put(i)
        try:              #捕获异常
            print(Yllo+"[*] 正在扫描%s"%self.target)
            thread_pool=[]  #设定一个线程池
            for i in range(0,int(self.threadnum)):
                th=threading.Thread(target=self.run,args=())
                thread_pool.append(th)
            for th in thread_pool:
                #setDaemon()方法。主线程A中，创建了子线程B，并且在主线程A中调用了B.setDaemon(),这个的意思是，把主线程A设置为守护线程，这时候，要是主线程A执行结束了，就不管子线程B是否完成,一并和主线程A退出.这就是setDaemon方法的含义，这基本和join是相反的。此外，还有个要特别注意的：必须在start() 方法调用之前设置，如果不设置为守护线程，程序会被无限挂起。
                th.setDaemon(True) 
                th.start()
            que.join()#实际上意味着等到队列为空，再执行别的操作
            print(Yllo+"[*] 完成扫描!!!")
        except Exception as e: #如果有异常，则输出异常，但不解决，继续执行
            print(e)   
            pass 
        except KeyboardInterrupt:   #接受用户
            print(RED+"[*] 用户自行退出扫描")
    
    def run(self):
        while not que.empty():
            port = int(que.get())     #从队列取值
            if self.portScan(port):   #调用portScan函数
                banner = self.getSocketBanner(port) 
                if banner:
                    print(GREE+"[*]%d%s------------open\t"%(port,banner))
                else:
                    print(GREE+"[*]%d------------open\t"%(port))
            que.task_done() #Queue.task_done() 在完成一项工作之后，Queue.task_done() 函数向任务已经完成的队列发送一个信号
#socket types：
#　SOCK_STREAM     TCP套接字类型
#　SOCK_DGRAM　　　 UDP套接字类型
#　SOCK_RAW        原始套接字类型，这个套接字比较强大,创建这种套接字可以监听网卡上的所有数据帧
#SOCK_RDM #是一种可靠的UDP形式，即保证交付数据报但不保证顺序。SOCK_RAM用来提供对原始协议的低级访问，在需要执行某些特殊操作时使用，如发送ICMP报文。SOCK_RAM通常仅限于高级用户或管理员运行的程序使用。
    def portScan(self,port):
        try:
#socket.socket(family=AF_INET, type=SOCK_STREAM, proto=0, fileno=None)         #创建socket对象
#socket families(地址簇)：AF_UNIX（unix本机之间进行通信），AF_INET（使用IPv4）AF_INET6（使用IPv6注）：socket.socket()中第一个能使用上述值。
            sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM) #定义套字节，设置（传输格式）地址簇为ipv4，类型为TCP套字节连接
            sk.settimeout(5) #设置返回时间限制为五秒
            if sk.connect_ex((self.target,port))==0:#sk.connect_ex是connect()函数的扩展版本,出错时返回出错码,而不是抛出异常，以主机元组的形式表示（host,port）成功返回0失败返回error
                return True
            else:
                 False
        except Exception as e:
            print("portsan:error",e)
            pass
        except KeyboardInterrupt:
            print(RED+"[*] 用户自行退出扫描")
            exit()
        finally:
            sk.close()  #关闭套字节
    def getSocketBanner(self,port):
        try:
            sk=socket.socket(socket.AF_INET,socket.SOCK_STREAM)
            sk.settimeout(0,5)
            sk.connect((self.target,port)) 
            sk.send("Hello\r\n".encode("utf-8")) #发送TCP数据。将string中的数据发送到连接的套接字，发送一个经过url编码的hello
            return sk.recv(20480).decode("utf-8") #接受TCP套接字的数据。数据以字符串形式返回，bufsize（2048）指定要接收的最大数据量
        except Exception as e:
            pass
        finally:
            sk.close()
        
parser = OptionParser()   #实例化对象
#添加选项的基本语法parser.add_option(opt_str, ...,  attr=value, ...)
#parser.add_option("-f", "--file", ...)  #-f 和 --file 是作为调用时的参数的标签，会被识别
#action有三种存储方式：store、store_false、store_true，默认的是store，它告诉optparse将继续读取下一个参数(type)，保证类型的正确性，并将它将值存储在一个变量（dest）中
#本文中 -p和--port 代表这行代码的标签，在接收到输入-p或--port时，会接受字符串型的值放在port中
parser.add_option('-p','--port',action="store",type="str",dest="port",help="All ports to be scanned default All port")
parser.add_option('-n','--num',action="store",type="int",dest="threadnum",help="Thread num default 100")
parser.add_option('-u','--dns',action="store",type="str",dest="target",help="输入域名")
#当选项被定义好后，则可以调用parse_args()函数来获取我们定义的选项和参数
#(options, args) = parser.parse_args() #parse_args可以有参数，不定义的话使用默认的sys.argv[1:]
#parse_args()返回两个值，一个是选项options（如：-f），另一个是参数args,即除选项options以外的值（如：test.txt） 
#如果我们输入的命令为 127.0.0.1 -p 443 (option,arg)接受的值分别为-p，127.0.0.1和443arg以列表的方式接受除option的值
(option,args)=parser.parse_args()
if option.target!=None:
    IP=[]
    f= open(option.target,'r')
    data2=f.readlines()
    f.close()
    print(data2)
    for i in data2:
        option.target=i
        option.target=option.target.strip('\n')
        print(option.target)
        if re.match(r"^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$",option.target):
        #逻辑思维判定 若果port和threadnum都没有值
            print(1)
            if  option.port == None and option.threadnum == None :
                scanner = Scanner(option.target,65535)  #把IP地址和端口号传入Scanner类中 Scanner中除self外，按顺序接收值。
                scanner.start() #调用Scanner类中的start函数
            elif option.port != None and option.threadnum ==None :
                port = option.port.split(',')# 以逗号为分隔符，把接受的option中的port值在列表中分割，放在port中                              
                scanner=Scanner(option.target,port)
                scanner.start()
            elif option.port == None and option.threadnum !=None :
                scanner=Scanner(option.target,65535,option.threadnum) #把线程数传入Scanner中，覆盖默认的线程数
                scanner.start()
            elif option.port != None and option.threadnum !=None :
                port = option.port.split(',')
                scanner = Scanner(option.target,port,option.threadnum)
                scanner.start()
            else:
                print(GREE+USAGE+GREE)
                parser.print_help()
        else:
            try:
                option.target=socket.gethostbyname(option.target)
                print(option.target)
                if  re.match(r"^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$",option.target):
                    if  option.port == None and option.threadnum == None :
                        scanner = Scanner(option.target,65535)  #把IP地址和端口号传入Scanner类中 Scanner中除self外，按顺序接收值。
                        scanner.start() #调用Scanner类中的start函数
                    elif option.port != None and option.threadnum ==None:
                        port = option.port.split(',')# 以逗号为分隔符，把接受的option中的port值在列表中分割，放在port中                              
                        scanner=Scanner(option.target,port)
                        scanner.start()
                    elif option.port == None and option.threadnum !=None:
                        scanner=Scanner(option.target,65535,option.threadnum) #把线程数传入Scanner中，覆盖默认的线程数
                        scanner.start()
                    elif option.port != None and option.threadnum !=None:
                        port = option.port.split(',')
                        scanner = Scanner(option.target,port,option.threadnum)
                        scanner.start()
                    else:
                        print(GREE+USAGE+GREE)
                        parser.print_help()
                else:
                    exit()
            except Exception as a:
                pass
    '''     finally:
                print("IP或域名输入不正确2222222222")
                exit()'''
elif re.match(r"^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$",args[0]):
        #逻辑思维判定 若果port和threadnum都没有值
    if  option.port == None and option.threadnum == None and len(args) ==1 :
        scanner = Scanner(args[0],65535)  #把IP地址和端口号传入Scanner类中 Scanner中除self外，按顺序接收值。
        scanner.start() #调用Scanner类中的start函数
    elif option.port != None and option.threadnum ==None and len(args) ==1:
        port = option.port.split(',')# 以逗号为分隔符，把接受的option中的port值在列表中分割，放在port中                              
        scanner=Scanner(args[0],port)
        scanner.start()
    elif option.port == None and option.threadnum !=None and len(args) ==1:
        scanner=Scanner(args[0],65535,option.threadnum) #把线程数传入Scanner中，覆盖默认的线程数
        scanner.start()
    elif option.port != None and option.threadnum !=None and len(args) ==1:
        port = option.port.split(',')
        scanner = Scanner(args[0],port,option.threadnum)
        scanner.start()
    else:
        print(GREE+USAGE+GREE)
        parser.print_help()
else:
    try:
        args[0]=socket.gethostbyname(args[0])
        if  re.match(r"^(25[0-5]|2[0-4]\d|[0-1]?\d?\d)(\.(25[0-5]|2[0-4]\d|[0-1]?\d?\d)){3}$",args[0]):
            if  option.port == None and option.threadnum == None and len(args) ==1 :
                scanner = Scanner(args[0],65535)  #把IP地址和端口号传入Scanner类中 Scanner中除self外，按顺序接收值。
                scanner.start() #调用Scanner类中的start函数
            elif option.port != None and option.threadnum ==None and len(args) ==1:
                port = option.port.split(',')# 以逗号为分隔符，把接受的option中的port值在列表中分割，放在port中                              
                scanner=Scanner(args[0],port)
                scanner.start()
            elif option.port == None and option.threadnum !=None and len(args) ==1:
                scanner=Scanner(args[0],65535,option.threadnum) #把线程数传入Scanner中，覆盖默认的线程数
                scanner.start()
            elif option.port != None and option.threadnum !=None and len(args) ==1:
                port = option.port.split(',')
                scanner = Scanner(args[0],port,option.threadnum)
                scanner.start()
            else:
                print(GREE+USAGE+GREE)
                parser.print_help()
        else:
            exit()
    except Exception as a:
        pass
    '''     finally:
                print("IP或域名输入不正确2222222222")
                exit()'''        
