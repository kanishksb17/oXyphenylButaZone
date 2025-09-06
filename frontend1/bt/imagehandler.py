import os
import shutil

class ImageHandler:
    def __init__(self, upload_folder="uploaded_images", placeholder_path="static/placeholder.png"):
        self.upload_folder = upload_folder
        self.placeholder_path = placeholder_path
        # Ensure upload folder exists
        os.makedirs(self.upload_folder, exist_ok=True)

    def save_image(self, image_file, filename):
        """
        Saves the uploaded image file to the upload folder.
        :param image_file: file-like object (opened in binary mode)
        :param filename: str - desired filename for saving
        :return: str - path to the saved image
        """
        dest_path = os.path.join(self.upload_folder, filename)
        with open(dest_path, "wb") as f:
            shutil.copyfileobj(image_file, f)
        return dest_path

    def get_image_path(self, filename=None):
        """
        Returns the path to the image.
        If filename is None or file does not exist, returns the placeholder path.
        :param filename: str or None
        :return: str - path to image or placeholder
        """
        if not filename:
            return self.placeholder_path
        img_path = os.path.join(self.upload_folder, filename)
        if os.path.exists(img_path):
            return img_path
        return self.placeholder_path

    def delete_image(self, filename):
        """
        Deletes an image file if it exists and is not the placeholder.
        :param filename: str
        :return: bool - True if deleted, False otherwise
        """
        img_path = os.path.join(self.upload_folder, filename)
        if os.path.exists(img_path) and img_path != self.placeholder_path:
            os.remove(img_path)
            return True
        return False

    def use_placeholder(self):
        """
        Returns the placeholder image path.
        """
        return self.placeholder_path