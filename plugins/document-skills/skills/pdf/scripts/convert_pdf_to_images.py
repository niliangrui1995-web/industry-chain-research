import os
import sys

from pdf2image import convert_from_path


MAX_PDF_PAGES = 100
PDF_RENDER_TIMEOUT_SECONDS = 120


def convert(pdf_path, output_dir, max_dim=1000, max_pages=MAX_PDF_PAGES):
    os.makedirs(output_dir, exist_ok=True)
    images = convert_from_path(
        pdf_path,
        dpi=200,
        first_page=1,
        last_page=max_pages,
        timeout=PDF_RENDER_TIMEOUT_SECONDS,
    )

    for i, image in enumerate(images):
        width, height = image.size
        if width > max_dim or height > max_dim:
            scale_factor = min(max_dim / width, max_dim / height)
            new_width = int(width * scale_factor)
            new_height = int(height * scale_factor)
            image = image.resize((new_width, new_height))
        
        image_path = os.path.join(output_dir, f"page_{i+1}.png")
        image.save(image_path)
        print(f"Saved page {i+1} as {image_path} (size: {image.size})")

    print(f"Converted {len(images)} pages to PNG images")


if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: convert_pdf_to_images.py [input pdf] [output directory]")
        sys.exit(1)
    pdf_path = sys.argv[1]
    output_directory = sys.argv[2]
    convert(pdf_path, output_directory)
