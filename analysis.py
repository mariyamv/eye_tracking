import pandas as pd


def do_analysis(gaze_data_path):
    data = pd.read_csv(gaze_data_path)
    print()


if __name__ == '__main__':
    do_analysis('./gaze_data.csv')
