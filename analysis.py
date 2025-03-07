import pandas as pd
import numpy as np
from PyGazeAnalyser.pygazeanalyser import detectors
from PyGazeAnalyser.pygazeanalyser import gazeplotter as gp
import math

# number of fixations
# mean fixation duration /sd

# number of sacaddeds
# mean length, sd
# k coeef for saccades

# bonus points for showing on a graph
def calculate_saccade_amplitude(x1, y1, x2, y2):
    return math.sqrt((x2 - x1) ** 2 + (y2 - y1) ** 2)


def do_analysis(gaze_data_path, image_path):

    data = pd.read_csv(gaze_data_path)

    x = np.array((data['Right_X'] + data['Left_X']) / 2) * 1440
    y = np.array((data['Right_Y'] + data['Left_Y']) / 2) * 900
    timestamps = np.array(data['Timestamp']) * 1000

    _, fixations = detectors.fixation_detection(x, y, timestamps)
    _, saccades = detectors.saccade_detection(x, y, timestamps)

    num_fixations = len(fixations)
    mean_fixation_duration = np.mean([fix[2] for fix in fixations])
    sd_fixation_duration = np.std([fix[2] for fix in fixations])
    num_saccades = len(saccades)
    mean_saccade_length = np.mean([sacc[2] for sacc in saccades])
    sd_saccade_length = np.std([sacc[2] for sacc in saccades])


    return {
        'num_fixations': num_fixations,
        'mean_fixation_duration': mean_fixation_duration,
        'sd_fixation_duration': sd_fixation_duration,
        'num_saccades': num_saccades,
        'mean_saccade_length': mean_saccade_length,
        'sd_saccade_length': sd_saccade_length,
    }


if __name__ == '__main__':
    do_analysis('20231207-202530/raw_gaze_data.csv', './sample.jpeg')
