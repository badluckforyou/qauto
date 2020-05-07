
class Document:
    """
    杂七杂八的文档
    """

    @classmethod
    def manual_of_folders(cls):
        return """
            
    stress_now文件夹的内容为当前使用的方案
    通过auto_test.py执行压力测试, 卸载与安装均写在其中, 游戏名、包名及apk名均写在其if __name__中
    fight2/fight2.py中的steps即为行为步骤
    
    stress_future文件夹的内容为后续调整方向
    django将其web页面传来的对应数据存到远端数据库, 通过parakimo连接对应的多个控制机, 再通过指令唤起docker
    唤起docker指令一般为(指令的具体含义查看commands_of_environments)
    docker run -it -v:/home/stress:/home/stress --cpuset-cpus='0' stress0:v0 sh -c [python commands]
    docker 会根据指令[python3, 文件名, 测试人员名, ip号, 端口数量]去执行调用的脚本:
        1.执行apk卸载和安装调用apkmanage.py
        2.执行压力测试调用stress.py
        两者需要传入的参数均为:
            数据库中存的测试人员名称, 用以查询需要用到的测试人员的对应数据 
                1.operation, apk, package
                2.game, resolution, retry_image, package, level, runtime
            ip号, ip号暂时有50个
            端口数量, 每个ip最大有60个端口数量, 即60部云手机
    
    备注:
    1.django的上传功能仅支持上传到django本地, 由于执行的控制机有多台, 且django不会布署在这多台控制机上
所以还需要将django本地的文件再利用paramiko转发到对应的控制机中。当然, 最好的方案还是直接将上传文件上传到 
多台控制机上, 跳过转存操作, 以达到最优效果
    2.stress_future暂未没有实现操作完成后的结果保存, 后续最好在操作完成后将结果状态存入到数据库中, 即对
finish.py进行调整
    3.django需要实现一个刷新状态的功能, 点击页面按钮就去数据库读取对应数据, 再将数据显示出来告知测试人员
"""

    @classmethod
    def commands_of_environments(cls):
        return """
yum -y install docker
systemctl daemon-reload
service docker restart

# 创建容器
docker build -t [name:version] .

# 查看历史运行容器
docker ps -a
# 删除历史运行容器记录
docker rm $(docker ps -a -q)
# 运行容器
docker run -it -v[linuxfilepath]:[dockerfilepath] --cpuset-cpus="0,1,2,3" autotest:v0.0.5 /bin/bash
# 进入正在运行的容器
docker attach 镜像ID
# 镜像保存为新容器
dcoker commit 镜像ID 镜像名:版本号
# 容器保存到本地, 一般为.rar后缀
docker save [name:version]>[filename(better ends with .rar)]
# 从本地导入容器
docker load<[filename]


# centos7安装adb
wget https://dl.google.com/android/repository/sdk-tools-linux-3859397.zip 
unzip sdk-tools-linux-3859397.zip
mkdir -p /opt/adb/
mv tools /opt/adb/

yum -y install lrzsz
yum -y install java-1.8.0-openjdk.x86_64
# http://downloads.puresoftware.org/files/android/platform-tools/ 下载对应的platforms
# 把platform上传到linux解压到/opt/adb
vi /etc/profile
# 在未尾加上下列3行
export PATH USER LOGNAME MAIL HOSTNAME HISTSIZE HISTCONTROL
export PATH=$PATH:/opt/adb/tools/bin
export PATH=$PATH:/opt/adb/platform-tools
# 保存退出再执行
source /etc/profile
# yum -y install ncurses-libs.i686 libstdc++.i686 libgcc.i686
adb --version


centos7安装python3
wget https://www.python.org/ftp/python/3.7.6/Python-3.7.6.tgz
yum -y install libffi-devel
yum -y install zlib zlib-devel
mkdir /opt/python3
./configure --perfix=/opt/python3
make && make install
ln -s /opt/python3/bin/python3 /usr/local/bin/python3
ln -s /opt/python3/bin/pip3 /usr/local/bin/pip3
"""

    @classmethod
    def manual_of_stress(cls):
        return """
如何配置后端?

首先将本工具stress.zip上传到云控制机/home文件夹下, 且文件夹名从stresstest改为stress

在工具中创建测试项目的文件夹A(如fight2)
在文件夹中A创建与文件夹名对应的python文件B(如fight2.py)
将/fight2/fight2.py中的内容复制到文件B中

对文件B中的steps内容进行修改

steps解释:
    # (点击, png文件, 是否需要一直等待(0是1否), 失败重试次数)
    # ("click "一键注册.png 0, 3),

    # (检查前面点击后面, png文件A, png文件B, 是否需要一直等待, 失败重试次数, 点击次数)
    # ("click_other "新手引导NPC.png "继续任务.png 0, 3, 20),

    # (检查前面点击后面, 检查前面点击后面, 坐标, 是否需要一直等待, 失败重试次数, 点击次数)
    # ("click_other "新手引导NPC.png (450, 200), 0, 3, 3),

    # (延时, 时长)
    # ("delay 100),

    # (写入, 内容(""表明写入预设值), 失败重试次数)
    # ("write " 0),

    # (记录, 内容(int类型会被当作等级记录, str类型会写入log中))
    # ("record 10),

将流程截图保存到文件夹A中
将安装包保存到文件夹A中

auto_test.py为测试过程控制文件, 
内置首次测试会自动安装打开和授权等, 二次测试只会直接尝试打开
开始测试时需要将其if __name__ == '__main__':下的game, package, apk改成自己要测试项目的

control.py为airtest行为封装文件, 测试时如果是自己输入角色名, 二次测试需要改动该文件207行中的字母

runtest.py为windows本地执行文件, 直接执行该文件即会唤起远端docker,
具体唤起数量可通过修改

"""

    @classmethod
    def dockerfile(cls):
        return """
# Dockerfile配置模板
FROM centos:7.2.1511

RUN yum -y install libffi-devel
RUN yum -y install zlib zlib-devel
RUN yum -y install make
RUN rpm -rebuilddb && yum -y install openssl-devel
RUN rpm -rebuilddb && yum -y install gcc unzip
RUN rpm -rebuilddb && yum -y install java-1.8.0-openjdk.x86_64
RUN rpm -rebuilddb && yum -y install ncurses-libs.i686 libgcc.i686

RUN mkdir /home/software
RUN mkdir /opt/python3
RUN mkdir /opt/adb

# add files to docker image
ADD Python.tgz /home/software
ADD requirements.txt /home/software
ADD platform-tools_r23.0.1-linux.zip /opt/adb
ADD sdk-tools-linux-3859397.zip /opt/adb

# install python3
WORKDIR /home/software/Python-3.7.6
RUN ./configure --prefix=/opt/python3
RUN make && make install

# set python3/pip3's hyperlink
RUN ln -s /opt/python3/bin/python3 /usr/local/bin/python3
RUN ln -s /opt/python3/bin/pip3 /usr/local/bin/pip3

# pip3 install requirements
RUN pip3 install -r /home/software/requirements.txt -i https://pypi.doubanio.com/simple

# unzip adb files
WORKDIR /opt/adb
RUN unzip platform-tools_r23.0.1-linux.zip
RUN unzip sdk-tools-linux-3859397.zip
RUN rm -rf platform-tools_r23.0.1-linux.zip
RUN rm -rf sdk-tools-linux-3859397.zip

# set adb env
RUN echo "export PATH USER LOGNAME MAIL HOSTNAME HISTSIZE HISTCONTROL" >> /etc/profile
RUN echo "export PATH=$PATH:/opt/adb/tools/bin" >> /etc/profile
RUN echo "export PATH=$PATH:/opt/adb/platform-tools" >> /etc/profile
RUN source /etc/profile

RUN mkdir /home/stress
WORKDIR /home/stress
"""

    @classmethod
    def common_issues(cls):
        return """
    
    1.接入sdk的包, 需确认同ip大量注册不会触发sdk的注册保护机制
    
    2.sdk的注册属于二级弹窗, 不能直接在steps里面写注册和登录, 可以在django添加"在'配置测试信息'的
'SDK弹窗关键字'中填入对应的点击关键字, 多个二级弹窗的关键字以英文逗号隔开, 如: 一键注册, 确定 "; 之
后再去stress_future中实现根据关键字来判定是否要用uiautomator来注册和登录
    
    3.apk最好为整包, 不然无法判定掉线是由于资源加载所导致的带宽问题还是游戏本身的问题
    
    4.随机名字可能会重复, 如果自己手动输入, 需要特殊处理

    5.压测的最终目的是"找到游戏最合适的同时在线人数及服务器所在机器需要用到什么样的配置 而不是简单的
达成N人同时在线, 目前由于时间和人力的不足, 且公司和项目组对这一块不太熟悉, 所以暂时只完成了达成人同时
在线, 如果你接手这个项目, 赞成这个设计思路, 可以在此基础上继续实现
"""
