import psutil

def SystemMonitor():
    def __init__(self):
        None
        
    def getCPULoad(self):
        return psutil.cpu_percent(interval=1)
    
    def getMemoryLoad(self):
        memory = psutil.virtual_memory()
        total_memory = memory.total 
        used_memory = memory.used
        
        return used_memory/total_memory
    
    def getTotalMemory(self):
        memory = psutil.virtual_memory()
        total_memory = memory.total
        
        #Conversie KB -> GB 
        return total_memory/(2**30)
    
    def getUsedMemory(self):
        memory = psutil.virtual_memory()
        used_memory = memory.used
    
        #Conversie KB -> GB 
        return total_memory/(2**30)
    
    def getTemperatureInfo(self):
        try:
            import subprocess
            temp_output = subprocess.run(["sensors"], capture_output=True, text=True)
            temp_lines = [line for line in temp_output.stdout.split("\n") if "temp" in line.lower()]
            temperature_info = temp_lines[0] if temp_lines else "Temperature info not available"
            
        except Exception:
            raise RuntimeError('Temperature Info stat is only available for Linux Operating System. '+
                               'If you are running on Linux you might have a missing module')
        
    def getTemperature(self,device):
        return psutil.sensors_temperatures()