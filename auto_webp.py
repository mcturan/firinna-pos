import os
from PIL import Image
import glob

def convert_to_webp(folder_path):
    print(f"Checking for images to convert in {folder_path}...")
    for ext in ('*.jpg', '*.png', '*.jpeg', '*.JPG', '*.PNG', '*.JPEG'):
        for img_path in glob.glob(os.path.join(folder_path, ext)):
            base, _ = os.path.splitext(img_path)
            webp_path = base + ".webp"
            if not os.path.exists(webp_path):
                try:
                    with Image.open(img_path) as img:
                        img.save(webp_path, 'webp', quality=80)
                    print(f"Auto-converted: {img_path} -> {webp_path}")
                    os.remove(img_path) # optionally delete original
                except Exception as e:
                    print(f"Error converting {img_path}: {e}")

if __name__ == '__main__':
    convert_to_webp('/opt/firinna-pos/web')
