import contextlib
import shutil
import tempfile
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage
from cStringIO import StringIO
from PIL import Image


@contextlib.contextmanager
def make_temp_directory():
    temp_dir = tempfile.mkdtemp()
    yield temp_dir
    shutil.rmtree(temp_dir)


image_file_format = {
    'image/png': 'PNG',
    'image/jpeg': 'JPEG',
}


def resize_uploaded_image(buf, width, height):
    # todo: temporary solution. need to create proper exception.
    assert buf.content_type in image_file_format, "Invalid image type. Only JPEG and PNG accepted."

    image = Image.open(buf)
    size = (width, height)
    image.thumbnail(size, Image.ANTIALIAS)

    resizedFile = StringIO()
    image.save(resizedFile, image_file_format[buf.content_type])
    resizedFile.seek(0)

    return resizedFile


def save_image(f, obj, img, name, dirname):
    if not f:
        return

    if hasattr(obj, img):
        try:
            default_storage.delete(getattr(obj, img))
        except:
            pass

    path = default_storage.save(dirname + getattr(obj, name) + '-' + f.name,
                                ContentFile(f.read()))

    try:
        setattr(obj, img, path)
        #some don't have setters, just ignore
    except:
        pass
    obj.save()


def save_thumb(f, obj, icon, name, dirname, width=40, height=40):
    """ for location types """

    if not f:
        return

    if (hasattr(obj, icon) and obj.icon):
        default_storage.delete(getattr(obj, icon))

    resizedImage = resize_uploaded_image(f, width, height)
    path = default_storage.save(dirname + getattr(obj, name) + '-' + f.name,
                                ContentFile(resizedImage.getvalue()))

    setattr(obj, icon, path)
    obj.save()


def convert(value, type, unit):
    if isinstance(value, basestring):
        value = value.replace(',', '')
        if not value.isnumeric():
            return value

    if type == 'weight':
        if unit in WEIGHT_CONVERSION :
            return float(value) * WEIGHT_CONVERSION[unit]
        else:
            return value
    elif type == 'length':
        if unit in LENGTH_CONVERSION:
            return float(value) * LENGTH_CONVERSION[unit]
        else:
            return value

WEIGHT_CONVERSION = {
    ('lb', 'oz'): 16,
    ('lb', 'kg'): 0.4536,
    ('lb', 'g'): 453.6,
    ('lb', 'ton'): 0.0004536,
    ('oz', 'lb'): 0.0625,
    ('oz', 'g'): 28.35,
    ('oz', 'kg'): 0.02835,
    ('oz', 'ton'): 0.00002835,
    ('ton', 'kg'): 1000,
    ('ton', 'g'): 1000000,
    ('ton', 'lb'): 2205,
    ('ton', 'oz'): 35270,
    ('kg', 'ton'): 0.001,
    ('kg', 'g'): 1000,
    ('kg', 'lb'): 2.205,
    ('kg', 'oz'): 35.27,
    ('g', 'ton'): 0.000001,
    ('g', 'kg'): 0.001,
    ('g', 'lb'): 0.002205,
    ('g', 'oz'): 0.03527
}

LENGTH_CONVERSION = {
    ('ft', 'in'): 12,
    ('ft', 'km'): 0.0003048,
    ('ft', 'm'): 0.3048,
    ('in', 'ft'): 0.08333,
    ('in', 'km'): 0.0000254,
    ('in', 'm'): 0.0254,
    ('km', 'm'): 1000,
    ('km', 'ft'): 3281,
    ('km', 'in'): 39370,
    ('m', 'km'): 0.001,
    ('m', 'ft'): 3.281,
    ('m', 'in'): 39.37
}
