def _rand_initialize_weights(self, size_in, size_out):
    return [((x * 0.12) - 0.06) for x in np.random.rand(size_out, size_in)]
        self.thata1 = self._rand_initialize_weights(400, num_hidden_nodes)
        self.thata2 = 