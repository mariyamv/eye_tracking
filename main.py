import json
import sys
import os

import tobii_research as tr
import pygame
import numpy as np
import csv
import time
from analysis import do_analysis

pygame.init()

WIDTH, HEIGHT = 3024 //2, 1964 //2
WHITE = (255, 255, 255)

# Initialize Pygame window
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.FULLSCREEN)
pygame.display.set_caption("Eye Gaze Plot")

# Lists to store gaze data
right_gaze_data_with_time = []
left_gaze_data_with_time = []


def load_and_scale_background(filename):
    image = pygame.image.load(filename)
    image_width, image_height = image.get_size()

    # Calculate the scaled dimensions while maintaining aspect ratio
    if image_width > WIDTH or image_height > HEIGHT:
        aspect_ratio = image_width / image_height
        if image_width > image_height:
            new_width = WIDTH
            new_height = int(WIDTH / aspect_ratio)
        else:
            new_height = HEIGHT
            new_width = int(HEIGHT * aspect_ratio)
        image = pygame.transform.scale(image, (new_width, new_height))

    return image


def gaze_data_callback(gaze_data):
    right_x, right_y = gaze_data['right_gaze_point_on_display_area']
    left_x, left_y = gaze_data['left_gaze_point_on_display_area']
    timestamp = time.time()

    # Handle NaN cases
    if not (np.isnan(right_x) or np.isnan(right_y)):
        right_gaze_data_with_time.append((timestamp, right_x, right_y))

    if not (np.isnan(left_x) or np.isnan(left_y)):
        left_gaze_data_with_time.append((timestamp, left_x, left_y))


def save_gaze_data_to_csv(filename):
    with open(filename, 'w', newline='') as csvfile:
        csv_writer = csv.writer(csvfile)
        csv_writer.writerow(['Timestamp', 'Right_X', 'Right_Y', 'Left_X', 'Left_Y'])  # Write header

        for (right_timestamp, right_x, right_y), (left_timestamp, left_x, left_y) in zip(right_gaze_data_with_time, left_gaze_data_with_time):
            csv_writer.writerow([right_timestamp, right_x, right_y, left_x, left_y])


def draw_dots():
    for (_, rx, ry), (_, lx, ly) in zip(right_gaze_data_with_time, left_gaze_data_with_time):
        if not np.isnan(rx) and not np.isnan(ry) and not np.isnan(lx) and not np.isnan(ly):
            x = (rx + lx) / 2
            y = (ry + ly) / 2
            pygame.draw.circle(screen, (0, 0, 0), (int(x * WIDTH), int(y * HEIGHT)), 2)


def main():
    if len(sys.argv) < 3:
        image_path = "./sample.jpeg"
        output_path_dir = time.strftime("%Y%m%d-%H%M%S")
    else:
        image_path = sys.argv[1]
        output_path_dir = sys.argv[2]

    background_image = load_and_scale_background(image_path)
    found_eyetrackers = tr.find_all_eyetrackers()
    my_eyetracker = found_eyetrackers[0]
    my_eyetracker.subscribe_to(tr.EYETRACKER_GAZE_DATA, gaze_data_callback, as_dictionary=True)

    running = True
    while running:
        for event in pygame.event.get():
            # End the Game
            if event.type == pygame.QUIT or (event.type == pygame.KEYDOWN and event.key == pygame.K_SPACE):
                os.makedirs(output_path_dir, exist_ok=True)
                pygame.image.save(screen, f'{output_path_dir}/drawing_with_image.png')
                pygame.display.flip()
                screen.fill(WHITE)
                draw_dots()
                pygame.image.save(screen, f'{output_path_dir}/drawing.png')
                running = False
                break

        # Clear the screen with white
        screen.fill(WHITE)

        # Draw the centered background image
        bg_x = (WIDTH - background_image.get_width()) // 2
        bg_y = (HEIGHT - background_image.get_height()) // 2
        screen.blit(background_image, (bg_x, bg_y))

        # Draw gaze points
        draw_dots()
        pygame.display.flip()



    my_eyetracker.unsubscribe_from(tr.EYETRACKER_GAZE_DATA, gaze_data_callback)
    save_gaze_data_to_csv(f'{output_path_dir}/raw_gaze_data.csv')
    analyzed_data = do_analysis(f'{output_path_dir}/raw_gaze_data.csv', image_path)
    analyzed_data = json.dumps(analyzed_data, indent=4)
    with open(f'{output_path_dir}/analyzed_data.json', 'w') as f:
        f.write(analyzed_data)

    pygame.quit()


if __name__ == "__main__":
    main()
