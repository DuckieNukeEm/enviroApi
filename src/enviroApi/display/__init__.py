import colorsys
import sys
import time
from st7735 import ST7735  # for the display
from fonts.ttf import RobotoMedium as UserFont
from PIL import Image, ImageDraw, ImageFont
from enviroApi.config import load_display_config

# Create ST7735 LCD display class


class Display:
    def __init__(self):
        self.st7735 = ST7735(
            port=0,
            cs=1,
            dc="GPIO9",
            backlight="GPIO12",
            rotation=270,
            spi_speed_hz=10000000,
        )
        self._init_screen()
        self._setup()
        self.Limits, self.RGB = load_display_config()

    def _init_screen(self):
        self.st7735.begin()
        self.width = self.st7735.width
        self.height = self.st7735.height

    def _setup(self):
        # Set up canvas and font
        self.img = Image.new("RGB", (WIDTH, HEIGHT), color=(0, 0, 0))
        self.draw = ImageDraw.Draw(img)
        self.font_size_small = 10
        self.font_size_large = 20
        self.font = ImageFont.truetype(UserFont, self.font_size_large)
        self.smallfont = ImageFont.truetype(UserFont, self.font_size_small)
        self.x_offset = 2
        self.y_offset = 2
        # The position of the top bar
        self.top_pos = 25

    def display_text(self, variable, data, unit):
        # NOTE: THIS DOES NOT WORK!!!!!
        # Maintain length of list
        values[variable] = values[variable][1:] + [data]
        # Scale the values for the variable between 0 and 1
        # TO DO - Normalize Text
        vmin = min(values[variable])
        vmax = max(values[variable])
        colours = [(v - vmin + 1) / (vmax - vmin + 1) for v in values[variable]]
        # Format the variable name and value
        # TO DO Set Message
        message = f"{variable[:4]}: {data:.1f} {unit}"
        logging.info(message)
        self.draw.rectangle((0, 0, self.WIDTH, self.HEIGHT), (255, 255, 255))
        for i in range(len(colours)):
            # Convert the values to colours from red to blue
            colour = (1.0 - colours[i]) * 0.6
            r, g, b = [int(x * 255.0) for x in colorsys.hsv_to_rgb(colour, 1.0, 1.0)]
            # Draw a 1-pixel wide rectangle of colour
            self.draw.rectangle((i, self.top_pos, i + 1, self.HEIGHT), (r, g, b))
            # Draw a line graph in black
            line_y = (
                self.HEIGHT
                - (self.top_pos + (colours[i] * (self.HEIGHT - self.top_pos)))
                + self.top_pos
            )
            self.draw.rectangle((i, line_y, i + 1, line_y + 1), (0, 0, 0))
        # Write the text at the top in black
        self.draw.text((0, 0), message, font=font, fill=(0, 0, 0))
        st7735.display(img)

    # Displays data and text on the 0.96" LCD


# Displays all the text on the 0.96" LCD
def display_everything():
    draw.rectangle((0, 0, WIDTH, HEIGHT), (0, 0, 0))
    column_count = 2
    row_count = len(variables) / column_count
    for i in range(len(variables)):
        variable = variables[i]
        data_value = values[variable][-1]
        unit = units[i]
        x = x_offset + ((WIDTH // column_count) * (i // row_count))
        y = y_offset + ((HEIGHT / row_count) * (i % row_count))
        message = f"{variable[:4]}: {data_value:.1f} {unit}"
        lim = limits[i]
        rgb = palette[0]
        for j in range(len(lim)):
            if data_value > lim[j]:
                rgb = palette[j + 1]
        draw.text((x, y), message, font=smallfont, fill=rgb)
    st7735.display(img)
