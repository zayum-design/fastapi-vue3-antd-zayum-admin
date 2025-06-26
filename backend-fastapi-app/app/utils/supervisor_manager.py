import subprocess
from xmlrpc.client import ServerProxy

class SupervisorManager:
    def __init__(self, service_name):
        self.service_name = service_name
        
    def via_command(self):
        """通过命令行重启"""
        try:
            subprocess.run(["supervisorctl", "restart", self.service_name], check=True)
            return True
        except subprocess.CalledProcessError:
            return False
            
    def via_xmlrpc(self):
        """通过 XML-RPC 重启"""
        try:
            server = ServerProxy('http://localhost:8000')
            server.supervisor.stopProcess(self.service_name)
            server.supervisor.startProcess(self.service_name)
            return True
        except Exception:
            return False
            
    def safe_restart(self):
        """自动选择可用方法"""
        return self.via_command() or self.via_xmlrpc()

# 使用示例
manager = SupervisorManager("my_fastapi_app")
if manager.safe_restart():
    print("服务重启成功")
else:
    print("所有重启方法均失败")