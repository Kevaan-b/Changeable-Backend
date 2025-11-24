import pytest
import shutil
from pathlib import Path

from my_flask_app.processors.ocr.easyocr_processor import EasyOCRProcessor
from my_flask_app.processors.typesetting.easyocr_typesetter import EasyOCRTypesetter

@pytest.mark.integration
def test_typesetting(image_path: Path, languages: list[str]):
    #ocr = EasyOCRProcessor(languages=languages) #when passing languages
    ocr = EasyOCRProcessor()
    typesetter = EasyOCRTypesetter()

    assert image_path.exists(), f"Image or directory not found: {image_path}"

    # Accept both a single image file or a directory
    if image_path.is_file():
        image_files = [image_path]
    else:
        image_files = sorted(
            list(image_path.glob("*.jpg")) +
            list(image_path.glob("*.png"))
        )

    assert image_files, f"No image files found in {image_path}"
    print(f"Found {len(image_files)} image(s) in {image_path}")

    output_dir = Path("./tests/masked_results")
    if output_dir.exists():
        shutil.rmtree(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    for img_path in image_files:
        print(f"\nProcessing {img_path.name}")
        try:
            text_data = ocr.extract_text(str(img_path))
            print(f"OCR extracted {len(text_data)} text regions.")
            for region in text_data[:5]:
                print(f"- {region['text']} (conf={region['confidence']:.3f})")

            output_path = output_dir / f"{img_path.stem}_replaced.jpg"
            result = typesetter.apply(str(img_path), text_data, output_path)
            print(f"Replaced image saved to {result}")

        except Exception as e:
            print(f"Error processing {img_path.name}: {e}")

    print(f"\nCompleted OCR + text replacement for {len(image_files)} images.")
    print(f"Results saved to: {output_dir.resolve()}")

if __name__ == "__main__":
    test_typesetting(Path("./tests/chapter_images/page_06.jpg"), ["vi"])  # Using a temporary path for testing