import base64
import os
import sqlite3
import zlib

import keras
import matplotlib.pyplot as plt
import numpy as np
import tensorflow as tf
from flask import Flask, jsonify, request
from flask_cors import CORS
from keras.models import Model

from tools import database, filemanager, image_editor

app = Flask(__name__)

# Server Config
CORS(app)

# database
db = sqlite3.connect("data.db")
cursor = db.cursor()
cursor.execute(
    """
CREATE TABLE IF NOT EXISTS users (
    id TEXT PRIMARY KEY,
    firstname TEXT NOT NULL,
    lastname TEXT NOT NULL,
    username TEXT NOT NULL UNIQUE,
    email TEXT NOT NULL UNIQUE,
    password TEXT NOT NULL
)
"""
)

cursor.execute(
    """
CREATE TABLE IF NOT EXISTS sessions (
    session_id TEXT PRIMARY KEY,
    userip TEXT NOT NULL,
    user_id TEXT NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
)
"""
)
db.commit()
db.close()


model_class = keras.models.load_model("./models/leucemie_balanced.keras")
model_seg_old = keras.models.load_model("./models/leucemie_seg.keras")
model_seg_new = keras.models.load_model("./models/leucemie_seg_final.keras")
model_chest = keras.models.load_model("./models/chest.keras")
model_kidney = keras.models.load_model("./models/kidney_stone.keras")
model_eye = keras.models.load_model("./models/eye_class.keras")
model_brain = keras.models.load_model("./models/brain_tumor_classifier.keras")


def getActivations(img_array, model, layer_type="conv"):
    img_tensor = tf.convert_to_tensor(img_array)
    layer_outputs = [
        layer.output for layer in model.layers if layer_type in layer.name
    ]
    activation_model = Model(inputs=model.inputs, outputs=layer_outputs)
    activations = activation_model.predict(img_tensor)
    return activations[0]


def getActivationsResNet(img_array, model, layer_type="conv4"):
    img_tensor = tf.convert_to_tensor(img_array)
    resnet_model = model.get_layer("resnet50")
    resnet_model.summary()
    layer_outputs = [
        layer.output
        for layer in resnet_model.layers
        if layer_type in layer.name
    ]
    activation_model = tf.keras.models.Model(
        inputs=resnet_model.input, outputs=layer_outputs
    )
    activations = activation_model.predict(img_tensor)
    return activations[0]


@app.route("/")
def hello_world():
    return "Server is Alive."


@app.route("/sign", methods=["POST"])
def singUp():
    print(request.form)
    username = request.form["username"]
    email = request.form["username"]
    if not database.checkUserExists(username, email):
        database.createUser(request.form)
    return "Thanks"


@app.route("/brain_mri", methods=["POST"])
def send_dummy():
    print(request.files)
    # t1 = filemanager.load_nii_file(request.files['images[0]'].stream)
    # t1c3 = filemanager.load_nii_file(request.files['images[1]'].stream)
    # t2 = filemanager.load_nii_file(request.files['images[2]'].stream)
    # flaiir = filemanager.load_nii_file(request.files['images[3]'].stream)
    img = filemanager.load_nii_file("./dummy/BraTS20_Training_001_seg.nii")
    _, img = np.unique(img, return_inverse=True)
    img = img.astype(np.uint8)

    compressed = zlib.compress(img.tobytes())
    b64_data = base64.b64encode(compressed).decode("utf-8")
    unique_values, counts = np.unique(img, return_counts=True)
    return jsonify(
        {"shape": img.shape, "dtype": str(img.dtype), "data": b64_data}
    )


@app.route("/eye", methods=["POST"])
def send_activations_eye():
    old_size = [(0, 0)]
    image_orig = filemanager.getClientImage(
        request.files["image"], mode="L", size=(512, 512), old_size=old_size
    )

    diagnostic = model_eye.predict(np.expand_dims(image_orig, axis=0))
    activations = getActivations(np.expand_dims(image_orig, axis=0), model_eye)

    size = activations.shape[3]
    result = {}
    for i in range(size):
        min_val = np.min(activations[0, :, :, i])
        max_val = np.max(activations[0, :, :, i])
        activation = image_editor.prepare_for_client(
            activations[0, :, :, i],
            mode="grayscale",
            norm=False,
            resize=old_size[0],
        )
        result[f"img_{i+1}"] = f"data:image/png;base64,{activation}"
        result[f"range_{i+1}"] = {"a": float(min_val), "b": float(max_val)}
    result["size"] = size
    result["probs"] = (diagnostic[0]).tolist()
    result["classes"] = [
        "Age-related Macular Degeneration",
        "Choroidal Neovascularization",
        "Central Serous Retinopathy",
        "Diabetic Macular Edema",
        "Diabetic Retinopathy",
        "Yellow deposits under the retina",
        "Macular Hole",
        "Healthy eyes with no abnormalities",
    ]

    return jsonify(result)


@app.route("/kidney", methods=["POST"])
def send_activations_kidney():
    old_size = [(0, 0)]
    image_orig = filemanager.getClientImage(
        request.files["image"],
        size=(256, 256),
        to_numpy=True,
        old_size=old_size,
    )

    image_orig = image_editor.change_range(image_orig)
    diagnostic = model_kidney.predict(np.expand_dims(image_orig, axis=0))
    activations = getActivations(
        np.expand_dims(image_orig, axis=0), model_kidney
    )

    size = activations.shape[3]
    result = {}
    for i in range(size):
        min_val = np.min(activations[0, :, :, i])
        max_val = np.max(activations[0, :, :, i])
        activation = image_editor.prepare_for_client(
            activations[0, :, :, i],
            mode="grayscale",
            norm=False,
            resize=old_size[0],
        )
        result[f"img_{i+1}"] = f"data:image/png;base64,{activation}"
        result[f"range_{i+1}"] = {"a": float(min_val), "b": float(max_val)}
    result["size"] = size
    prob = (diagnostic[0]).tolist()[0]
    result["probs"] = [1 - prob, prob]
    result["classes"] = ["Normal", "Kidney Stone"]

    return jsonify(result)


@app.route("/brain", methods=["POST"])
def send_activations_brain():
    old_size = [(0, 0)]
    image_orig = filemanager.getClientImage(
        request.files["image"],
        size=(512, 512),
        to_numpy=True,
        mode="L",
        scale=True,
        old_size=old_size,
    )
    diagnostic = model_brain.predict(np.expand_dims(image_orig, axis=0))
    activations = getActivations(
        np.expand_dims(image_orig, axis=0), model_brain
    )
    size = activations.shape[3]
    result = {}
    for i in range(size):
        min_val = np.min(activations[0, :, :, i])
        max_val = np.max(activations[0, :, :, i])
        activation = image_editor.prepare_for_client(
            activations[0, :, :, i],
            mode="grayscale",
            norm=False,
            resize=old_size[0],
        )
        result[f"img_{i+1}"] = f"data:image/png;base64,{activation}"
        result[f"range_{i+1}"] = {"a": float(min_val), "b": float(max_val)}
    result["size"] = size
    result["probs"] = (diagnostic[0]).tolist()
    result["classes"] = ["glioma", "meninigioma", "notumor", "pituary"]

    return jsonify(result)


@app.route("/chest", methods=["POST"])
def send_activations_chest():
    old_size = [(0, 0)]
    image_orig = filemanager.getClientImage(
        request.files["image"],
        size=(256, 256),
        to_numpy=True,
        old_size=old_size,
    )
    image_orig = image_editor.histogram_equalization(image_orig)
    diagnostic = model_chest.predict(np.expand_dims(image_orig, axis=0))
    activations = getActivationsResNet(
        np.expand_dims(image_orig, axis=0), model_chest
    )
    print(activations.shape)
    size = activations.shape[3]
    result = {}
    for i in range(size):
        min_val = np.min(activations[0, :, :, i])
        max_val = np.max(activations[0, :, :, i])
        activation = image_editor.prepare_for_client(
            activations[0, :, :, i],
            mode="grayscale",
            norm=False,
            resize=old_size[0],
        )
        result[f"img_{i+1}"] = f"data:image/png;base64,{activation}"
        result[f"range_{i+1}"] = {"a": float(min_val), "b": float(max_val)}
    result["size"] = size
    result["probs"] = (diagnostic[0]).tolist()
    result["classes"] = ["COVID", "LUNG OPACITY", "NORMAL", "PNEUMONIA"]

    return jsonify(result)


@app.route("/all", methods=["POST"])
def analyze_all():
    image_orig = filemanager.getClientImage(
        request.files["image"],
        size=(224, 224),
    )
    img_filtered = image_editor.leuk_read(image_orig)
    image_keep = np.asarray(image_orig)
    image_orig = image_editor.to_numpy(image_orig)

    diagnostic = model_class.predict(np.expand_dims(image_keep, axis=0))
    mask1 = model_seg_old.predict(
        np.expand_dims(
            np.dot(image_orig[..., :3], [0.2989, 0.5870, 0.1140]), axis=0
        )
    )
    mask2 = model_seg_new.predict(np.expand_dims(img_filtered, axis=0))
    mean_mask = np.mean(np.array([mask1, mask2]), axis=0)
    smooth = image_editor.smooth_mask(image_orig, mask2[0, :, :, 0])

    mask1 = image_editor.prepare_for_client(mask1[0, :, :, 0], mode="grayscale")
    mask2 = image_editor.prepare_for_client(mask2[0, :, :, 0], mode="grayscale")
    mean_mask = image_editor.prepare_for_client(
        mean_mask[0, :, :, 0], mode="grayscale"
    )
    smooth = image_editor.prepare_for_client(smooth, mode="grayscale")

    return jsonify(
        {
            "size": 4,
            "img_1": f"data:image/png;base64,{mask1}",
            "img_2": f"data:image/png;base64,{mask2}",
            "img_3": f"data:image/png;base64,{mean_mask}",
            "img_4": f"data:image/png;base64,{smooth}",
            "probs": (diagnostic[0]).tolist(),
            "classes": [
                "Benign",
                "Early Leukemia",
                "Pre-B/T ALL",
                "Pro-B/T ALL",
            ],
        }
    )


@app.route("/all_activ", methods=["POST"])
def send_activations_all():
    image_orig = filemanager.getClientImage(
        request.files["image"],
        size=(224, 224),
    )

    diagnostic = model_class.predict(np.expand_dims(image_orig, axis=0))
    activations = getActivations(
        np.expand_dims(image_orig, axis=0), model_class
    )

    size = activations.shape[3]
    result = {}
    for i in range(size):
        min_val = np.min(activations[0, :, :, i])
        max_val = np.max(activations[0, :, :, i])
        activation = image_editor.prepare_for_client(
            activations[0, :, :, i], mode="grayscale", norm=False
        )
        result[f"img_{i+1}"] = f"data:image/png;base64,{activation}"
        result[f"range_{i+1}"] = {"a": float(min_val), "b": float(max_val)}
    result["size"] = size
    result["probs"] = (diagnostic[0]).tolist()
    result["classes"] = [
        "Benign",
        "Early Leukemia",
        "Pre-B/T ALL",
        "Pro-B/T ALL",
    ]

    return jsonify(result)


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8080, debug=True)
