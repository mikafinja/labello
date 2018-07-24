from PIL import Image, ImageDraw, ImageFont
from brother_ql.devicedependent import models, label_type_specs, ENDLESS_LABEL, cuttingsupport, min_max_length_dots
from brother_ql import BrotherQLRaster, create_label
from brother_ql.backends import backend_factory
from io import BytesIO, StringIO
import base64
from . import font, backend, logger, config
import qrcode
from .halftone import halftone


class Label:
    def __init__(self, data, file=False):
        """ creates a new label with the given settings """
        lts = label_type_specs
        self.size = data['label_size']
        self.width, self.height = lts[self.size]['dots_printable']
        if "font_name" not in data:
            data['font_name'] = "OCRA"
        if "font_size" not in data:
            data['font_size'] = 42
        font_path = font.fonts[data['font_name']]
        font_size = 45
        if data['orientation'] == 'rotated':
            self.rotated = True
        else:
            self.rotated = False
        self.data = data

        if not file:
            self.font_path = font_path
            self.font_size = font_size
            self.font = ImageFont.truetype(
                font.fonts[data['font_name']]['path'], int(data['font_size']))
        self.image = Image.new('L', (self.width, self.height), 255)
        self.label = ImageDraw.Draw(self.image)
        logger.debug('Rotated: {}'.format(self.rotated))
        if 'text' in self.data:
            self.text()
        if 'qr_text' in self.data:
            self.qr()
        if file:
            self.img(file)

    def convert_to_png(self):
        img_buf = BytesIO()
        self.image.save(img_buf, format="PNG")
        img_buf.seek(0)
        return base64.b64encode(img_buf.getbuffer())

    def scale(self, dim):
        img_height, img_width = dim

        # set width and height
        if self.height == 0:
            label_height = dim[0]
        else:
            label_height = self.height
        label_width = self.width

        if self.rotated:
            if img_width > label_height or img_height > label_width:
                ratio = min(label_height / img_width, label_width / img_height)
                x = ratio * img_height
                y = ratio * img_width
            else:
                y = img_height
                x = img_width

        else:
            if img_width > label_width or img_height > label_height:
                ratio = min(label_width / img_width, label_height / img_height)
                x = ratio * img_height
                y = ratio * img_width
            else:
                x = img_height
                y = img_width

        ret = (int(x), int(y))

        logger.debug('Scaled image: {}'.format(ret))

        return ret

    def img(self, img):
        img = Image.open(img)
        logger.debug('Generating label from image.')
        logger.debug('Data: {}'.format(self.data))
        logger.debug('Image: {}'.format(img))
        logger.debug('Image size: {}'.format(img.size))
        imgsize = self.scale(img.size)
        logger.debug('Scaled image size: {}'.format(imgsize))

        # resize label
        rot_img = False
        if self.height == 0:
            if self.rotated:
                x = self.width
                y = imgsize[1]
            else:
                x = imgsize[0]
                y = self.width
        else:
            if self.rotated:
                y = self.height
                x = self.width
            else:
                x = self.height
                y = self.width

        self.image = Image.new('L', (x, y), 255)

        logger.debug('Label dimensions: {}, {}'.format(x, y))
        logger.debug('Scaled dimensions: {}'.format(imgsize))

        self.label = ImageDraw.Draw(self.image)

        img = halftone(img.resize(imgsize), 8, 1, 45)
        self.image.paste(img, (0, 0))

    def qr(self):
        logger.debug('Generating QR-CODE: {}'.format(self.data['qr_text']))

        # TODO: more options on qr-code (Error-Correction, plaintext content, etc)
        if 'error_correction' in self.data:
            error_correction = self.data['error_correction']
        else:
            error_correction = 0

        qr = qrcode.QRCode(version=1,
                                error_correction=error_correction,
                                box_size=10,
                                border=1
                                )

        qr.add_data(self.data['qr_text'])
        qr.make()
        qrimage = qr.make_image(fill_color="black", back_color="white")

        qrsize = self.scale(qrimage.size)

        logger.debug('QR Size: {}'.format(qrsize))

        # resize label
        if self.height == 0:
            if self.rotated:
                x = qrsize[1]
                y = self.width
            else:
                y = qrsize[0]
                x = self.width
        else:
            if self.rotated:
                y = self.width
                x = self.height
            else:
                x = self.width
                y = self.height

        self.image = Image.new('L', (x, y), 255)
        self.label = ImageDraw.Draw(self.image)
        logger.debug('Label dimensions: {}, {}'.format(x, y))
        logger.debug('Scaled dimensions: {}'.format(qrsize))
        qrimage = qrimage.resize(qrsize)

        self.image.paste(qrimage, (0, 0))

    def text(self):
        x, y = self.label.multiline_textsize(self.data['text'], font=self.font)

        # resize label
        if self.height == 0:
            if self.rotated:
                self.height = self.width
                self.width = x
            else:
                self.height = y
        elif self.rotated:
            self.height, self.width = label_type_specs[self.size]['dots_printable']
        self.image = Image.new('L', (self.width, self.height), 255)
        self.label = ImageDraw.Draw(self.image)

        # horizontal alignment
        if self.data['halign'] == "center":
            x = int(self.width/2) - int(x / 2)
        elif self.data['halign'] == "left":
            x = 0
        elif self.data['halign'] == "right":
            x = self.width - x

        # vertical alignment
        if self.data['valign'] == "middle":
            y = int(self.height / 2) - int(y / 2)
        elif self.data['valign'] == "top":
            y = 0
        elif self.data['valign'] == "bottom":
            y = self.height - y
        self.label.multiline_text(
            (x, y), self.data['text'], 0, font=self.font, align=self.data['halign'])

    def draw(self):
        return self.convert_to_png()

    def prt(self):
        print(label_type_specs[self.size])
        if label_type_specs[self.size]['kind'] == ENDLESS_LABEL:
            rot = 0 if not self.rotated else 90
        else:
            rot = 'auto'

        if label_type_specs[self.size]['kind'] != 2:
            label_type_specs[self.size]['feed_margin'] = config['label']['feed_margin']

        qlr = BrotherQLRaster(config['printer']['model'])
        if config['printer']['model'] in cuttingsupport:
            logger.debug('Printer is capable of automatic cutting.')
            cutting = True
        else:
            logger.debug('Printer is not capable of automatic cutting.')
            cutting = False
        create_label(qlr, self.image, self.size,
                     threshold=30, cut=cutting, rotate=rot)
        try:
            backend_class = backend_factory(backend)['backend_class']
            be = backend_class(config['printer']['device'])
            be.write(qlr.data)
            be.dispose()
            del be
            return "alert-success", "<b>Success:</b>Label printed"
        except Exception as e:
            logger.warning("unable tp print")
            logger.warning(e)
            return "danger", "unable to print"
