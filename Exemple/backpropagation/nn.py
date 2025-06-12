import numpy as np

def softmax(x):
    x = x - np.max(x, axis=1, keepdims=True)
    e_x = np.exp(x)
    return e_x / np.sum(e_x, axis=1, keepdims=True)

def relu(x):
    return np.maximum(0, x)

def relu_derivative(x):
    return (x > 0).astype(float)

def categorical_cross_entropy(y_true, y_pred, epsilon=1e-12):
    y_pred = np.clip(y_pred, epsilon, 1. - epsilon)
    return -np.mean(np.sum(y_true * np.log(y_pred), axis=1))


class Layer:
    def __init__(self, input_size, size, name, activation=None):
        self.size = size
        self.weight = np.random.randn(input_size, size) * np.sqrt(2. / input_size)
        self.bias = np.zeros(size)
        self.name = name
        self.activation = activation

    def forwardpass(self, inputs):
        z = inputs.dot(self.weight) + self.bias
        return self.activation(z) if self.activation else z

    def summary(self):
        print(f'{self.name}({self.size})')


class MLP:
    def __init__(self, input_size, output_size, layer_sizes):
        if not layer_sizes:
            raise Exception('No hidden layers')

        self.input_size = input_size
        self.output_size = output_size
        self.layers = []

        self.layers.append(Layer(input_size, layer_sizes[0], 'Hidden 1', activation=relu))
        for i in range(1, len(layer_sizes)):
            self.layers.append(Layer(layer_sizes[i-1], layer_sizes[i], f'Hidden {i+1}', activation=relu))

        self.output = Layer(layer_sizes[-1], output_size, 'Output', activation=None)

    def summary(self):
        print(f'Input({self.input_size})')
        for layer in self.layers:
            layer.summary()
        self.output.summary()

    def forwardpass(self, inputs):
        for layer in self.layers:
            inputs = layer.forwardpass(inputs)
        logits = self.output.forwardpass(inputs)
        return softmax(logits)

    def backwardpass(self, x, y, lr):
        activations = [x]
        layer_inputs = []
        current = x

        for layer in self.layers:
            z = current.dot(layer.weight) + layer.bias
            layer_inputs.append(z)
            current = layer.activation(z) if layer.activation else z
            activations.append(current)

        z_out = current.dot(self.output.weight) + self.output.bias
        layer_inputs.append(z_out)
        output = softmax(z_out)

        error = (output - y)

        grad_weight = activations[-1].T.dot(error)
        grad_bias = np.mean(error, axis=0)
        self.output.weight -= lr * grad_weight
        self.output.bias -= lr * grad_bias

        error = error.dot(self.output.weight.T)
        for i in reversed(range(len(self.layers))):
            layer = self.layers[i]
            d_activation = relu_derivative(layer_inputs[i])
            error *= d_activation

            grad_weight = activations[i].T.dot(error)
            grad_bias = np.mean(error, axis=0)

            layer.weight -= lr * grad_weight
            layer.bias -= lr * grad_bias


            error = error.dot(layer.weight.T)

        final_output = self.forwardpass(x)
        return categorical_cross_entropy(y, final_output)

    def fit(self, train_dataset, test_dataset=None, epochs=30, learning_rate=1e-5, verbose=True):
        for epoch in range(epochs):
            total_loss = 0
            for x, y in zip(train_dataset.x, train_dataset.y):
                loss = self.backwardpass(x, y, learning_rate)
                if np.isnan(loss):
                    print("NaN loss detected. Aborting training.")
                    return
                total_loss += loss

            avg_loss = total_loss / len(train_dataset.x)

            if verbose:
                print(f'Epoch {epoch + 1}/{epochs}, Loss: {avg_loss:.4f}')
                if test_dataset:
                    acc = self.evaluate(test_dataset)
                    print(f'Test Accuracy: {acc:.2f}%')

    def evaluate(self, dataset):
        correct = 0
        total = 0
        for x, y in zip(dataset.x, dataset.y):
            pred = self.forwardpass(x)
            correct += np.sum(np.argmax(pred, axis=1) == np.argmax(y, axis=1))
            total += x.shape[0]
        return (correct / total) * 100
    