from Neuron import Neuron
import numpy as np


def relu(x):
    return np.maximum(0, x)


def sigmoid(x):
    return 1 / (1 + np.exp(-x))


class Network:
    def __init__(self):
        # Create 4 neurons for hidden layer, each with 4 inputs
        self.hidden_layer = [Neuron(4) for _ in range(4)]

        self.hidden_layer2 = [Neuron(4) for _ in range(4)]

        # Create output neuron with 4 inputs
        self.output_neuron = Neuron(4)

    def forward(self, bird_height, bird_velocity, distance, gap_height):
        """
        Pass inputs through the network and return output
        """
        inputs = np.array([bird_height, bird_velocity, distance, gap_height])

        # Compute hidden layer outputs
        hidden_outputs = []
        for neuron in self.hidden_layer:
            # Compute weighted sum: sum(input * weight) + bias
            z = np.dot(neuron.weights, inputs) + neuron.bias
            activation = relu(z)
            hidden_outputs.append(activation)

        hidden_outputs = np.array(hidden_outputs)

        second_hidden_outputs = []
        for neuron in self.hidden_layer2:
            z = np.dot(neuron.weights, hidden_outputs) + neuron.bias
            activation = relu(z)
            second_hidden_outputs.append(activation)

        second_hidden_outputs = np.array(second_hidden_outputs)

        # Compute output neuron
        z_output = np.dot(self.output_neuron.weights, second_hidden_outputs) + self.output_neuron.bias
        output = sigmoid(z_output)

        return output

    def mutate(self, mutation_rate=0.1, mutation_strength=0.5):
        # Mutate hidden layer
        for neuron in self.hidden_layer:
            if np.random.rand() < mutation_rate:
                neuron.weights += np.random.normal(0, mutation_strength, size=neuron.weights.shape)
                neuron.bias += np.random.normal(0, mutation_strength)

        for neuron in self.hidden_layer2:
            if np.random.rand() < mutation_rate:
                neuron.weights += np.random.normal(0, mutation_strength, size=neuron.weights.shape)
                neuron.bias += np.random.normal(0, mutation_strength)

        # Mutate output neuron
        if np.random.rand() < mutation_rate:
            self.output_neuron.weights += np.random.normal(0, mutation_strength, size=self.output_neuron.weights.shape)
            self.output_neuron.bias += np.random.normal(0, mutation_strength)
