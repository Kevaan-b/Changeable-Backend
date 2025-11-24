from abc import ABC, abstractmethod
from pathlib import Path


class Typesetter(ABC):
    """
    Abstract base class for typesetters.

    Implementations should take OCR output (list of dicts with at least a 'bbox' and 'text')
    and write an output image with the desired typesetting applied.
    """

    @abstractmethod
    def apply(self, image_path: str, ocr_data: list[dict], out_path: Path) -> str:
        """Apply typesetting to the image based on OCR data and save the result."""
        raise NotImplementedError
