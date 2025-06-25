import numpy as np
import keras
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.metrics import confusion_matrix, accuracy_score

dir_original_data = "../dataIN/Leucemie/Original"
model_path = "../dataOUT/leucemie_balanced.keras"

model = keras.models.load_model(model_path)
model.summary()
model_seg = keras.models.load_model(model_path)

test_dataset = keras.utils.image_dataset_from_directory(
    dir_original_data,
    labels="inferred",
    label_mode='categorical',
    validation_split=0.2,
    subset='validation',
    seed=42,
    image_size=(224, 224)
)

predictions = []
real_labels = []

for images, labels in test_dataset:
    preds = model.predict(images)
    predictions.extend(np.argmax(preds, axis=1)) 
    real_labels.extend(np.argmax(labels.numpy(), axis=1)) 

cm = confusion_matrix(real_labels, predictions)

plt.figure(figsize=(8, 6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=range(4), yticklabels=range(4))
plt.xlabel('Predicted Label')
plt.ylabel('True Label')
plt.title('Confusion Matrix')
plt.show()

accuracy = accuracy_score(real_labels, predictions)
print(f"Accuracy: {accuracy:.2%}")