import numpy as np


class Neuron:
    def __init__(self, num_inputs: int):
        self.num_inputs = num_inputs
        self.weights = None
        self.bias = 0
        self.initialise_weights()

    def initialise_weights(self):
        # He initialization for weights
        self.weights = np.random.randn(self.num_inputs) * np.sqrt(2 / self.num_inputs)
        # Initialize bias with small random value (not 0)
        # This gives the network some initial behavior
        self.bias = np.random.randn() * 0.5
