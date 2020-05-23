"""
File: ct_scan.py
----------------
This program

1.  Locates and highlights lung inflammation areas in a CT scan.
2.  Counts the number of cases and identifies which lung is
    affected: left, right or both.
3.  Calculates inflammation demotions, diameter, and area when
    a user points at the located areas with cursor.

*** HOW IT WORKS ***

1.  Crops an uploaded image to 400x300 size.
2.  Converts the image into black and white.
3.  Identifies all the potential areas (between INTENSITY_MIN
    and INTENSITY_MAX) and highlights them with green
    (pixel.green = 255).
4.  Scans the entire image and compares the intensity of green
    across all the areas.
5.  Measures the contrast of the image and based on that sets
    sensitivity min and max.
6.  Highlights with red the areas whose average intensity
    of green is within the sensitivity min and max.
7.  Adds all such areas to the image with green highlights.
8.  Transfers all the red ares to the image of the original size
    and removes all the green highlights.
9.  Calculates the number of cases and which lungs they're located in.
10. Converts the images into a canvas.
11. Prompts a user to measure the highlighted inflammation areas
    with cursor (click, pull, release).
12. Prints the dimensions, diameter, and area.
"""

from simpleimage import SimpleImage
import tkinter
from PIL import ImageTk
import math

INTENSITY_MIN = 210
INTENSITY_MAX = 245
AREA_SIZE = 100
STEP_SIZE = 50
IMAGE_WIDTH = 400
IMAGE_HEIGHT = 300

def main():

    filename = get_file()
    original_image = SimpleImage(filename)
    original_image.show()
    cropped_image = crop_image(original_image)
    green_highlights = highlight_areas(cropped_image)
    green_highlights.show()
    red_highlights_and_case_count = find_cases(green_highlights)
    red_highlights = red_highlights_and_case_count[0]
    case_count = red_highlights_and_case_count[1]
    red_highlights.show()
    final_image = remove_green(red_highlights, filename)
    final_image.show()
    print_report(final_image, case_count)
    measure_cases(final_image, case_count)

def crop_image(image):
    # Crops an image to the size of 400x300 cutting equal number of pixels from each side
    width = image.width
    height = image.height
    if width == IMAGE_WIDTH and height == IMAGE_HEIGHT:
        return image
    else:
        new_width = IMAGE_WIDTH
        new_height = IMAGE_HEIGHT
        new_image = SimpleImage.blank(new_width, new_height)
        for x in range(new_width):
            for y in range(new_height):
                old_x = x + (width - new_width) // 2
                old_y = y + (height - new_height) // 2
                pixel = image.get_pixel(old_x, old_y)
                new_image.set_pixel(x, y, pixel)
    return new_image

def highlight_areas(image):
    # Applies black and white filter to the original image
    # Checks intensity of average against INTENSITY_MIN and INTENSITY_MAX
    # Highlights all the pixels in that range with green
    for pixel in image:
        average = (pixel.red + pixel.green + pixel.blue) // 3
        pixel.red = pixel.green = pixel.blue = average
        if INTENSITY_MIN <= average <= INTENSITY_MAX:
            pixel.red = 0
            pixel.green = 255
            pixel.blue = 0
    return image

def find_cases(image):
    # Scans the image with a 100x100 "viewfinder"
    # Highlights each inflammation area with a red square
    # Adds all the red areas to the image
    case_count = 0
    for x in range(0, image.width - AREA_SIZE // 2, STEP_SIZE):
        for y in range(0, image.height - AREA_SIZE // 2, STEP_SIZE):
            scanned_area = get_area(image, x, y)
            scan_results = scan_area(scanned_area, image)
            red_area = scan_results[0]
            case_count += scan_results[1]
            image = add_area(image, red_area, x, y)
    return image, case_count

def get_area(image, n, m):
    # Gets and returns an area of 100x100
    area = SimpleImage.blank(AREA_SIZE, AREA_SIZE)
    for y in range(AREA_SIZE):
        for x in range(AREA_SIZE):
            pixel = image.get_pixel((x + n), (y + m))
            area.set_pixel(x, y, pixel)
    return area

def scan_area(area, image):
    # Checks the contrast of the image and sets sensitivity min and max
    # Checks the average green of the entire image against sensitivity min and max
    # If the average is within the sensitivity min and max, marks the borders of the area with red
    # Counts number of cases
    case_count = 0
    area_green_avg = get_green_agv(area)
    image_green_avg = get_green_agv(image)
    if 80 < image_green_avg < 85:
        sensitivity_min = 108
        sensitivity_max = 110
    elif 130 < image_green_avg < 135:
        sensitivity_min = 140
        sensitivity_max = 142
    elif 105 < image_green_avg < 110:
        sensitivity_min = 186
        sensitivity_max = 188
    else:
        sensitivity_min = 10
        sensitivity_max = 20
    if sensitivity_min <= area_green_avg <= sensitivity_max:
        case_count += 1
        highlight = SimpleImage.blank(AREA_SIZE, AREA_SIZE)
        for x in range(AREA_SIZE):
            for y in range(AREA_SIZE):
                pixel = area.get_pixel(x, y)
                highlight.set_pixel(x, y, pixel)
                if pixel.y == 0 or pixel.y == AREA_SIZE - 1 or pixel.x == 0 or pixel.x == AREA_SIZE - 1:
                    pixel.red = 255
                    pixel.green = 0
                    pixel.blue = 0
    return area, case_count

def get_green_agv(image):
    # Gets average green of an image
    # Adds up all the values of green and then divides the sum by the image area in pixels
    width = image.width
    height = image.height
    green_tot = 0
    green_highlights = 0
    for pixel in image:
        if pixel.green != 255:
            green_tot += pixel.green
        else:
            green_highlights += 1
    green_avg = green_tot // ((width * height) - green_highlights)
    return green_avg

def add_area(image, red_area, n, m):
    # Takes the cropped image
    # Adds all red area to the image
    new_image = SimpleImage.blank(image.width, image.height)
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.get_pixel(x, y)
            new_image.set_pixel(x, y, pixel)
    for x in range(AREA_SIZE):
        for y in range(AREA_SIZE):
            pixel = image.get_pixel(x, y)
            new_image.set_pixel(x, y, pixel)
            pixel = red_area.get_pixel(x, y)
            new_image.set_pixel(x + n, y + m, pixel)
    return new_image

def remove_green(image, filename):
    # Takes the image of the original size and adds all red areas to it
    new_image = SimpleImage(filename)
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.get_pixel(x, y)
            if pixel.red == 255:
                new_image.set_pixel(x + (new_image.width - IMAGE_WIDTH) // 2, y + (new_image.height - IMAGE_HEIGHT) // 2, pixel)
    return new_image

def print_report(image, case_count):
    # Calls tot_cases to find the number of cases found
    # Prints the number of cases and their location
    tot_cases = locate_cases(image)
    if len(tot_cases) == 1:
        print("\n" + str(case_count) + " case found: " + str(tot_cases[0]) + " lung.")
    elif len(tot_cases) > 1:
        print("\n" + str(case_count) + " cases found: " + str(tot_cases[0]) + " and " + str(tot_cases[1]) + " lungs.")
    else:
        print("\n" + str(case_count) + " cases found.")

def locate_cases(image):
    # Locates the cases: right, left or both lungs
    # Creates an empty list for each of the lungs
    # Creates an empty list with total cases
    # Searches for red pixels and appends the 'left' or 'right' lists if found on the left or right side
    # If the lists aren't empty, appends 'tot_cases' list with 'left', 'right' or both.
    left = []
    right = []
    tot_cases = []
    for x in range(image.width):
        for y in range(image.height):
            pixel = image.get_pixel(x, y)
            if pixel.x < image.width//2 and pixel.red == 255 and pixel.green == 0 and pixel.blue == 0:
                left.append(pixel.x)
            elif pixel.x > image.width//2 and pixel.red == 255 and pixel.green == 0 and pixel.blue == 0:
                right.append(pixel.x)
    if left:
        tot_cases.append("left")
    if right:
        tot_cases.append("right")
    return tot_cases

def measure_cases(final_image, case_count):
    # Converts SimpleImage into canvas
    # Prompts a user to measure the highlighted inflammations with a mouse
    # Tracks left clicks and sends the events to 'button_clicked' to take measurements
    # Tracks a right click and sends the event to 'quit_program' to quit
    canvas = make_canvas(final_image.width, final_image.height)
    image = ImageTk.PhotoImage(final_image.pil_image)
    canvas.create_image(0, 0, anchor="nw", image=image)
    if case_count != 0:
        print("\nClick, pull and release to measure.")
        canvas.bind("<Button-1>", lambda event_left_click: button_clicked(event_left_click, canvas))
    print("Right click to exit...")
    canvas.bind("<Button-2>", lambda event_right_click: quit_program(canvas))
    canvas.mainloop()

def button_clicked(event_click, canvas):
    # Tracks button release and sends the events to 'button_released'
    canvas.bind("<ButtonRelease-1>", lambda event_release: button_released(event_release, event_click.x, event_click.y))

def button_released(event_release, x_start, y_start):
    # Collects coordinates of event_left_click and event_release and calls take_measurements
    x_end = event_release.x
    y_end = event_release.y
    take_measurements(x_start, y_start, x_end, y_end)

def take_measurements(x_start, y_start, x_end, y_end):
    # Takes start and end coordinates and calculates inflammation dimensions, diameter and area
    # (1 pixel = 1 mm for simplicity)
    # Prints all the results
    side_x = abs(x_end - x_start)
    side_y = abs(y_end - y_start)
    diameter = int(math.sqrt(side_x**2 + side_y**2))
    area = side_x * side_y
    print("\nDimensions: " + str(side_x) + " by " + str(side_y) + " mm")
    print("Diameter: " + str(diameter) + " mm")
    print("Area: " + str(area) + " mm")

def quit_program(canvas):
    # Closes the program after a right click
    print("\nThank you and stay safe!")
    canvas.quit()

def get_file():
    # Prompts user to input image address of or choose from presets
    filename = input('Enter a file name or a patient ID (1, 2, or 3): ')
    if filename == '1':
        filename = 'images/ct-scan.png'
    elif filename == '2':
        filename = 'images/ct-scan-2.jpg'
    elif filename == '3':
        filename = 'images/ct-scan-6.png'
    return filename

######## DO NOT MODIFY ANY CODE BELOW THIS LINE ###########

# This function is provided to you and should not be modified.
# It creates a window that contains a drawing canvas that you
# will use to make your drawings.
def make_canvas(width, height, title=None):
    """
    DO NOT MODIFY
    Creates and returns a drawing canvas
    of the given int size with a blue border,
    ready for drawing.
    """
    objects = {}
    top = tkinter.Tk()
    top.minsize(width=width, height=height)
    if title:
        top.title(title)
    canvas = tkinter.Canvas(top, width=width + 1, height=height + 1)
    canvas.pack()
    return canvas

if __name__ == '__main__':
    main()