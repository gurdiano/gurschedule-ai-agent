class ModelGenerationError(Exception):
    def __init__(self, n_attempts):
        self.n_attempts = n_attempts

        super().__init__(f'GeminiAPI failed after {n_attempts} attempts to retrieve a response from the model! Try again later.')