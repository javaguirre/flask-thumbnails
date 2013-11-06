import os
from PIL import Image, ImageOps
import errno


def _get_name(name, fm, *args):
    s = name

    for v in args:
        if v:
            s += '_%s' % v
    s += fm

    return s


class Thumbnail(object):
    def __init__(self, app=None):
        if app is not None:
            self.app = app
            self.init_app(self.app)
        else:
            self.app = None

    def init_app(self, app):
        # TODO: add default path app directory
        self.app = app
        app.config.setdefault('UPLOAD_FOLDER', None)

        app.jinja_env.filters['thumbnail'] = self.thumbnail

    def thumbnail(self, img_path, size, crop=None, bg=None, quality=100):
        """

        :param img_url: url path - '/home/user/assets/media/summer.jpg'
        :param size: size return thumb - '100x100'
        :param crop: crop return thumb - 'fit' or None
        :param bg: tuple color or None - (255, 255, 255, 0)
        :param quality: JPEG quality 1-100
        :return: :thumb_url:
        """
        width, height = [int(x) for x in size.split('x')]
        file_path, img_name = os.path.split(img_path)
        name, fm = os.path.splitext(img_name)
        miniature = _get_name(name, fm, size, crop, bg, quality)

        original_filepath = img_path
        thumb_filepath = os.path.join(self.app.config['UPLOAD_FOLDER'], miniature)

        # create folders
        self._get_path(thumb_filepath)

        thumb_url = os.path.join(
            self.app.static_url_path,
            self.app.config['UPLOAD_FOLDER'].replace(self.app.static_folder + '/', ''),
            miniature
        )

        if os.path.exists(thumb_filepath):
            return thumb_url

        elif not os.path.exists(thumb_filepath):
            thumb_size = (width, height)
            try:
                image = Image.open(original_filepath)
            except IOError:
                return None
            #image = image.convert('RGBA')
            if crop == 'fit':
                img = ImageOps.fit(image, thumb_size, Image.ANTIALIAS)
            else:
                img = image.copy()
                img.thumbnail((width, height), Image.ANTIALIAS)

            if bg:
                img = self._bg_square(img, bg)

            img.save(thumb_filepath, image.format, quality=quality)

            return thumb_url

    def _bg_square(self, img, color=0xff):
        size = (max(img.size),) * 2
        layer = Image.new('L', size, color)
        layer.paste(img, tuple(map(lambda x: (x[0] - x[1]) / 2, zip(size, img.size))))
        return layer

    def _get_path(self, full_path):
        directory = os.path.dirname(full_path)

        try:
            if not os.path.exists(full_path):
                os.makedirs(directory)
        except OSError as e:
            if e.errno != errno.EEXIST:
                raise
