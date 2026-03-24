from ocr_easy import extract_text_from_image, extract_text
from preprocessing import preprocess

# Use your project image path
image_path = "model fine tuning images/img1.jpeg"

print("\n===== OCR OUTPUT (path OCR) =====\n")
print(extract_text(image_path))

for mode in ["basic", "adaptive"]:
    print(f"\n===== OCR OUTPUT (preprocess mode: {mode}) =====\n")
    processed = preprocess(image_path, mode=mode)
    print(extract_text_from_image(processed))
