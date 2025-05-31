from keras.src.callbacks import Callback
from .logger import Logger
import tensorflow as tf

class LogCallback(Callback):
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

class EvaluateCERCallback (Callback):
    def __init__(self, val_dataset, decode_fn, idx_to_char):
        self.val_dataset = val_dataset
        self.decode_fn = decode_fn
        self.idx_to_char = idx_to_char

    def on_epoch_end(self, epoch, logs=None):
        y_true = []
        y_pred = []

        for batch in self.val_dataset:
            images = batch["image"]
            labels = batch["label"]

            preds = self.model.predict(images)
            decoded = self.decode_fn(preds)  
            true_labels = self.decode_fn(labels.numpy())

            y_pred.extend(decoded)
            y_true.extend(true_labels)

        cer_score = cer(y_true, y_pred)
        wer_score = wer(y_true, y_pred)
        print(f"\nEpoch {epoch+1} — CER: {cer_score:.2%}, WER: {wer_score:.2%}")