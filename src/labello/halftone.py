from PIL import Image, ImageDraw, ImageStat


def halftone(img, sample, scale, angle=45):
    img_grey = img.convert('L')
    channel = img_grey.split()[0]
    channel = channel.rotate(angle, expand=1)
    size = channel.size[0]*scale, channel.size[1]*scale

    new_img = Image.new('1', size)
    draw = ImageDraw.Draw(new_img)

    for x in range(0, channel.size[0], sample):
        for y in range(0, channel.size[1], sample):
            box = channel.crop((x, y, x+sample, y+sample))
            mean = ImageStat.Stat(box).mean[0]
            diameter = (mean/255) ** 0.5
            edge = 0.5 * (1-diameter)
            x_pos, y_pos = (x+edge) * scale, (y+edge) * scale
            box_edge = sample * diameter * scale
            draw.ellipse((x_pos, y_pos, x_pos+box_edge, y_pos+box_edge),
                         fill=255)

    new_img = new_img.rotate(-angle, expand=1)
    width_half, height_half = new_img.size
    half_x = (width_half - img.size[0]*scale) / 2
    half_y = (height_half - img.size[1]*scale) / 2
    new_img = new_img.crop((half_x, half_y, half_x + img.size[0]*scale,
                                  half_y + img.size[1]*scale))
    return Image.merge('1', [new_img])