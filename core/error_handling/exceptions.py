class CustomValidationError(Exception):
    """Custom exception that carries error code information"""
    def __init__(self, error_code, detail=None):
        self.error_code = error_code
        self.detail = detail or error_code.description
        super().__init__(f"{error_code.code}: {error_code.title}: {self.detail}")