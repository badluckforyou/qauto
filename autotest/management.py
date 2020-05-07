import re
import time

from math import ceil
from datetime import datetime

from autotest.database import DataBaseManage
from autotest.remote import CommandIssue
from autotest.app_settings import AppSettings

# 每个云手机集共有60部手机, 但建议最多只用45个
EACH_DOCKER_DEVICES = 45
TOTAL_DEVICES = EACH_DOCKER_DEVICES * 10 * 5


def time_without_bracket():
    """返回2019-12-25 17:21:06格式的时间"""
    return datetime.now().strftime("%Y-%m-%d %X")


class DockerNumberError(Exception):
    """docker数量不足"""
    pass

class DeviceNumberError(Exception):
    """云手机数量不足"""
    pass



class Management:

    INUSE = dict()
    RUNTIME = dict()
    FREE_DOCKERS = dict()

    @classmethod
    def set_status_of_user(cls, user):
        cls.INUSE[user] = True

    @classmethod
    def reset_status_of_user(cls, user):
        cls.INUSE[user] = False

    @classmethod
    def check_dockers_for_test(cls):
        """检查dockers是不是被占用, 有哪些没被占用"""
        pattern = re.compile(r"\w+:\w+")
        for ip in AppSettings.IPS.keys():
            ssh = CommandIssue(ip)
            ssh.connect()
            sshout = ssh.execute("docker ps")
            # 如果docker ps返回的内容只有一个元素
            # 则表明未有在执行的docker
            # 可以直接将docker全部放到FREE_DOCKERS[ip]中
            if len(sshout) == 1:
                cls.FREE_DOCKERS[ip] = AppSettings.IPS[ip]
                ssh.close()
                continue
            # 如果docker ps返回了具体的docker
            # 则需要检查docker name是否在AppSettings.IPS[ip]中
            # 存在则不放入到FREE_DOCKERS[ip]中
            dockers = AppSettings.IPS[ip]
            for line in sshout:
                find_docker = pattern.findall(line)
                if not line or not find_docker:
                    continue
                docker = find_docker[0]
                if docker in AppSettings.IPS[ip]:
                    dockers.pop(docker)
            cls.FREE_DOCKERS[ip] = dockers
            ssh.close()

    @classmethod
    def get_free_dockers_number(cls):
        """useall=True情况下, 获取空闲docker的数量"""
        number = 0
        if cls.FREE_DOCKERS:
            for v in cls.FREE_DOCKERS.values():
                if isinstance(v, list):
                    number += len(v)
        return number

    @classmethod
    def get_need_dockers_number(cls, number):
        """useall=Flase情况下, 获取要用到docker的数量"""
        if number <= EACH_DOCKER_DEVICES:
            return 1
        return number // EACH_DOCKER_DEVICES

    @classmethod
    def check_dockers_divisible(cls, number):
        """检查下需求设备能否平分到各个docker中"""
        free_number = cls.get_free_dockers_number()
        result = number % free_number
        return True if result == 0 else False

    @classmethod
    def check_devices_divisible(cls, number):
        """检查下需要设备是否正好为docker最大设备数的倍数"""
        if number < EACH_DOCKER_DEVICES:
            return True
        return True if number % EACH_DOCKER_DEVICES == 0 else False

    @classmethod
    def check_devices_for_start(cls, user, number):
        """
        检查devices数量是否足够, 检查为双重检查
            检查docker数量
            检查数据库表中存放adb状态字段INUSE为true的数量
        """
        number = int(number)
        cls.check_dockers_for_test()
        # 先检查docker的数量是否足够
        free_dockers_number = cls.get_free_dockers_number()
        if free_dockers_number * EACH_DOCKER_DEVICES < number:
            raise DockerNumberError("Dockers are not enough.")
        # 可能有其他部门在占用着云手机, 需要再检查下云手机的数量是否足够
        db = DataBaseManage()
        # inuse_number如果为None, 具表示没有正在使用中的云手机
        inuse_number = db.select("autotest_devicestatus", "ADDRESS", "INUSE='true'")
        if inuse_number is False:
            raise ConnectionError("Can't connect to MySQL server.")
        elif inuse_number is not None and TOTAL_DEVICES - len(inuse_number) < number:
            raise DeviceNumberError("Devices are not enough.")

    @classmethod
    def start_test(cls, module_file, user, number, useall=True):
        """
        唤起远端docker开始执行压测, 提供两种方案
        useall=True: 
            将number平分, 单次直接唤起全部可用docker
            此方案优点为减少单docker的压力, 提升压测效率
        useall=False:
            尽量将单docker的云手机开满后, 再去调用其它docker
            此方案优点为更适合多人同时使用压测
        """
        number = int(number)
        if useall is True:
            cls.run_with_all_docker(module_file, user, number)
        elif useall is False:
            cls.run_with_full_docker(module_file, user, number)
        else:
            raise ValueError("The value of 'useall' is not True or False, it's {}" % useall)
        cls.set_status_of_user(user)

    @classmethod
    def run_with_all_docker(cls, module_file, user, number):
        """
        使用全部空闲docker进行压测
        先进行余数判断, 再根据返回决定具体的执行方案
        """
        dockers = cls.get_free_dockers_number()
        if cls.check_dockers_divisible(number) is True:
            normal_docker_number = number // dockers
            cls.run_when_divisible(module_file, user, number, dockers, normal_docker_number)
        else:
            normal_docker_number = number // (dockers - 1)
            last_docker_number = number % (dockers - 1)
            cls.run_when_indivisible(module_file, user, number, dockers, normal_docker_number, last_docker_number)

    @classmethod
    def run_with_full_docker(cls, module_file, user, number):
        """
        将单docker的最大数量台云手机压满后, 再尝试调用别的docker
        """
        dockers = cls.get_need_dockers_number(number)
        normal_docker_number = EACH_DOCKER_DEVICES
        if cls.check_devices_divisible(number) is True:
            cls.run_when_divisible(module_file, user, number, dockers, normal_docker_number)
        else:
            last_docker_number = number % EACH_DOCKER_DEVICES
            cls.run_when_indivisible(module_file, user, number, dockers, normal_docker_number, last_docker_number)

    @classmethod
    def run_when_divisible(cls, module_file, user, number, dockers, ports):
        """如果可以直接整除, 就直接使用传入的ports"""
        count = 0
        for ip in cls.FREE_DOCKERS.keys():
            ssh = CommandIssue(ip)
            ssh.connect()
            for cpu, ip_number, docker_name in cls.FREE_DOCKERS[ip]:
                count += 1
                # 监控在docker数量
                if count > dockers:
                    break
                ssh.execute((
                    "docker run -it -v:/home/stress:/home/stress "
                    "--cpuset-cpus=%(cpu)s %(docker)s sh -c python3 "
                    "%(module)s run %(user)s %(ip_number)s %(ports)s"
                ) % {
                    "module": module_file,
                    "cpu": cpu,
                    "docker": docker_name,
                    "user": user,
                    "ip_number": ip_number,
                    "ports": ports,
                })
            ssh.close()
            if count > dockers:
                break

    @classmethod
    def run_when_indivisible(cls, module_file, user, number, dockers, normal_ports, last_ports):
        """如果可以不能直接整除, 最后一个docker要用余数"""
        count = 0
        for ip in cls.FREE_DOCKERS.keys():
            ssh = CommandIssue(ip)
            ssh.connect()
            for cpu, ip_number, docker_name in cls.FREE_DOCKERS[ip]:
                count += 1
                # 对当前docker与总docker进行判断
                # 如果当前docker为最后一个docker, ports要使用余数
                if count < dockers:
                    ports = normal_ports
                elif count == dockers:
                    ports = last_ports
                elif count > dockers:
                    break
                ssh.execute((
                    "docker run -it -v:/home/stress:/home/stress "
                    "--cpuset-cpus=%(cpu)s %(docker)s sh -c python3 "
                    "%(module)s run %(user)s %(ip_number)s %(ports)s"
                ) % {
                    "module": module_file,
                    "cpu": cpu,
                    "docker": docker_name,
                    "user": user,
                    "ip_number": ip_number,
                    "ports": ports,
                })
            ssh.close()
            if count > dockers:
                break

    @classmethod
    def watching(cls, user, runtime=2):
        """执行状态的监控, 单人同时只能进行一项测试"""
        cls.RUNTIME[user] = int(runtime) * 60
        time.sleep(cls.RUNTIME[user])
        cls.reset_status_of_user(user)
