from keras.src.callbacks import Callback
from logger import Logger

def LogCallback(Callback):
    def __init__(self,logger:Logger):
        self.logger = logger
    
    def on_epoch_end(self, epoch, logs=None):
        if logs==None:
            logger.warn("Metrics could not be logged")
        
        train_loss = logs.get("loss", -1)
        train_acc = logs.get("accuracy", -1)
        val_loss = logs.get("val_loss", -1)
        val_acc = logs.get("val_accuracy", -1)
        
        log_entry = f"{epoch+1},{train_loss:.4f},{train_acc:.4f},{val_loss:.4f},{val_acc:.4f}\n"

        logger.print(log_entry)
        