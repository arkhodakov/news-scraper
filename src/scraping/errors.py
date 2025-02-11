class ExtractionError(Exception):
    """Exception raised when the extraction of a URL fails."""

    url: str
    details: str

    def __init__(self, url: str, details: str):
        self.url = url
        self.details = details
        super().__init__(f"Error extracting {url}: {details}")
