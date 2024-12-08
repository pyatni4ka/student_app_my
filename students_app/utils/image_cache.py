import os
import hashlib
from PIL import Image

class ImageCache:
    def __init__(self, cache_dir='cache'):
        self.cache_dir = cache_dir
        if not os.path.exists(self.cache_dir):
            os.makedirs(self.cache_dir)

    def _get_cache_path(self, image_url):
        hash_object = hashlib.md5(image_url.encode())
        filename = hash_object.hexdigest() + '.jpg'
        return os.path.join(self.cache_dir, filename)

    def is_cached(self, image_url):
        cache_path = self._get_cache_path(image_url)
        return os.path.exists(cache_path)

    def get_cached_image(self, image_url):
        if self.is_cached(image_url):
            cache_path = self._get_cache_path(image_url)
            return Image.open(cache_path)
        return None

    def cache_image(self, image_url, image):
        cache_path = self._get_cache_path(image_url)
        image.save(cache_path)

    def clear_cache(self):
        for filename in os.listdir(self.cache_dir):
            file_path = os.path.join(self.cache_dir, filename)
            if os.path.isfile(file_path):
                os.unlink(file_path)