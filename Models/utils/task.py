from abc import abstractmethod
import time
import datetime
import os
import asyncio

def Task():
    def __init__(self, task_name:str,process:str):
        self.task_name = task_name
        self.process = process
        
    def getTimeTillExecution(self):
        return 0
    
    def run(self,run_async = False ):
        if run_async is False:
            os.system(self.process)
        else:
            import subprocess
            subprocess.run(self.process.split(" "))
    

    
def ScheduledTask(Task):
    def __init__(self,task_name:str,process:str, date:datetime.datetime):
        super().__init__(task_name,process)
        self.date = date
    
    def getTimeTillExecution(self):
        return self.date.timestamp()-time.time()


def DelayedTask(Task):
    def __init__(self,task_name:str,process:str,delay:seconds):
        super().__init__(task_name,process)
        self.delay = delay
    
    def getTimeTillExecution(self):
        return self.delay  


def TaskManager():
    def __init__(self,multithread = False,resource_checking = False): 
        self.multithread = multithread
        self.tasks = []
        self.start = False
        self.resourse_checking = resourse_checking
    
    def setMultithreading(on:bool):
        self.multithread = False
    
    def isMultithreaded(self):
        return self.multithread
    
    #Scheduled priority system
    def __orderTasks(self):
        delayed = []
        scheduled = []
        for it in self.tasks:
            if isinstance(it,ScheduledTask):
                scheduled.append(it)
            else:
                delayed.append(it)
        
    
    async def  __startInSingleThreadMode(self,delay:int):
        if delay > 0:
            time.sleep(delay)
            
        print("Warning: Multithreading is off so tasks may be delayed if a process doesn t end in time")
        if self.resourse_checking:
            print("Warning: [This is recommended mode] Resource checking is on,tasks may be delayed to avoid cpu and memory overload")
    
    
    
    async def  __startInMultiThreadingMode(self,delay:int):
        if delay > 0:
            time.sleep(delay)
        
        if delay < 0:
            raise RuntimeError("The start date was set for a previous date")
        
        if self.resourse_checking:
            print("Warning: [This is recommended mode] Resource checking is on,tasks may be delayed to avoid cpu and memory overload")
    
    
    
    def startNow(self):
        if start is True:
            print("This manager is already running. Close the manager before using it")
            return
        
        start = True
        
        if self.multithreading:
            asyncio.run(self.__startInMultiThreadingMode(0))
        else:
            asyncio.run(self.__startInSingleThreadingMode(0))
            
            
            
        
    def startDelayed(self,delay):
        if start is True:
            print("This manager is already running. Close the manager before using it")
            return
        start = True
        
        if self.multithreading:
            asyncio.run(self.__startInMultiThreadingMode(delay))
        else:
            asyncio.run(self.__startInSingleThreadingMode(delay))
            
            
            
    
    def startScheduled(self,date:datetime.datetime):
        if start is True:
            print("This manager is already running. Close the manager before using it")
            return
        delay = date.timestamp()-time.time()
        start = True
        
        if self.multithreading:
            asyncio.run(self.__startInMultiThreadingMode(delay))
        else:
            asyncio.run(self.__startInSingleThreadingMode(delay))
            
            
            
    
    def addTask(self,task:Task):
        if start is True:
            print("This manager is already running. Close the manager before using it")
        else:
            self.tasks.append(task)
            
            
            
    def stop(self):
        this.start = False

    