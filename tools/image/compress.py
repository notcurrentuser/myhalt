from PIL import Image


def compress_img(image, image_name):
    img = Image.open(image)

    img = img.resize((640, 640), Image.ANTIALIAS)
    img.save(image_name, quality=80, optimize=True)
