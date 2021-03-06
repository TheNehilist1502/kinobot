import logging
import subprocess

from PIL import Image, ImageOps

logger = logging.getLogger(__name__)


def get_magick(image):
    """Here I use a custom imagemagick script to get ten colors (check the
    scripts folder)"""
    image.save("/tmp/tmp_palette.png")
    output = subprocess.check_output(["paleta", "/tmp/tmp_palette.png"]).decode()[:-1]
    colors = output.split("\n")
    return [tuple([int(i) for i in color.split(",")]) for color in colors]


def get_magick_arch(image):
    " Variant for Arch Linux "
    image.save("/tmp/tmp_palette.png")
    output = (
        subprocess.check_output(["paleta", "/tmp/tmp_palette.png"])
        .decode()[:-1]
        .split("\n")
    )
    colors = []
    for i in output:
        new = [int(new_color.split(".")[0]) for new_color in i.split(",")]
        colors.append(tuple(new))
    return colors


def check_palette(colors):
    " try to make the best color palette possible "
    logger.info("Checking palette...")
    if len(colors) < 6:
        return
    # we can never know how many colors imagemagick will return
    # this loop checks wether a color is too white or not
    for color in range(len(colors)):
        if color < 5:
            continue
        hits = 0
        for tup in colors[color]:
            if tup > 175:
                hits += 1
        if hits > 2:
            return colors[:color]
        logger.info("hits for color {}: {}".format(color + 1, hits))
    return colors


# return frame + palette (PIL object)
def getPalette_legacy(img):
    width, height = img.size
    try:
        colors = get_magick(img)
    except ValueError:
        return img
    palette = check_palette(colors)
    if not palette:
        return img
    if len(palette) < 8:
        return img
    logger.info(palette)
    # calculate dimensions and generate the palette
    # get a nice-looking size for the palette based on aspect ratio
    divisor = (height / width) * 5.5
    heightPalette = int(height / divisor)
    divPalette = int(width / len(palette))
    offPalette = int(divPalette * 0.925)
    bg = Image.new("RGB", (width - int(offPalette * 0.2), heightPalette), "white")

    # append colors
    next_ = 0
    try:
        for color in range(len(palette)):
            if color == 0:
                imgColor = Image.new(
                    "RGB", (int(divPalette * 0.925), heightPalette), palette[color]
                )
                bg.paste(imgColor, (0, 0))
                next_ += divPalette
            else:
                imgColor = Image.new("RGB", (offPalette, heightPalette), palette[color])
                bg.paste(imgColor, (next_, 0))
                next_ += divPalette
        Paleta = bg.resize((width, heightPalette))

        # draw borders and append the palette
        Original = img

        borders = int(width * 0.0075)
        bordersT = (borders, borders, borders, heightPalette + borders)

        borderedOriginal = ImageOps.expand(Original, border=bordersT, fill="white")
        borderedPaleta = ImageOps.expand(Paleta, border=(0, borders), fill="white")

        borderedOriginal.paste(borderedPaleta, (borders, height))
        return borderedOriginal
    except TypeError:
        return img


def getPalette(imagen):
    try:
        colors = get_magick(imagen)
    except ValueError:
        return imagen
    palette = check_palette(colors)
    if not palette:
        return imagen
    logger.info(palette)
    w, h = imagen.size
    border = int(w * 0.03)
    if float(w / h) > 2.1:
        border = border - int((w / h) * 4)
    new_w = int(w + (border * 2))
    divPalette = int(new_w / len(palette))
    bg = Image.new("RGB", (new_w, border), "white")
    next_ = 0
    try:
        for color in range(len(palette)):
            if color == 0:
                imgColor = Image.new("RGB", (divPalette, border), palette[color])
                bg.paste(imgColor, (0, 0))
                next_ += divPalette
            elif color == len(palette) - 1:
                leftover = int((w - (divPalette * (len(palette) - 1))) / 2)
                imgColor = Image.new(
                    "RGB", (divPalette + leftover, border), palette[color]
                )
                bg.paste(imgColor, (next_, 0))
                next_ += divPalette
            else:
                leftover = int((w - (divPalette * 9)) / 2)
                imgColor = Image.new("RGB", (divPalette, border), palette[color])
                bg.paste(imgColor, (next_, 0))
                next_ += divPalette
        bordered = ImageOps.expand(
            imagen, border=(border, border, border, 0), fill=palette[0]
        )
        bordered.paste(bg, (0, int(h)))
        return bordered
    except TypeError:
        return imagen
