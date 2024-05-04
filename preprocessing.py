import random
from typing import List, Tuple

import numpy as np

import cv2
import librosa
import pickle
import librosa.display

data = pickle.load(open("annotation_test.pkl", "rb"), encoding='latin1')
print(data['extraversion']['_0bg1TLPP-I.000.mp4'])
print(data['neuroticism']['_0bg1TLPP-I.000.mp4'])
print(data['agreeableness']['_0bg1TLPP-I.000.mp4'])
print(data['conscientiousness']['_0bg1TLPP-I.000.mp4'])
print(data['openness']['_0bg1TLPP-I.000.mp4'])

def audio_preprocessing(audiopath):
    y, sr = librosa.load(audiopath)
    n, m = 20, 1000
    mfccs = librosa.feature.mfcc(y=y, sr=sr)
    standardized_mfccs = (mfccs - np.mean(mfccs)) / np.std(mfccs)
    n_fill = m - standardized_mfccs.shape[1]
    zeros = np.zeros((n, n_fill))
    filled_data = np.hstack((zeros, standardized_mfccs))
    return filled_data.reshape(n, m, 1)

def get_number_of_frames(videopath):
    cap = cv2.VideoCapture(videopath)
    frames_num = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    return frames_num

def extract_videoframes(filepath, samples_num: int = 6):
    frames_num = get_number_of_frames(filepath)
    videoframes = []
    frames = random.sample(range(0, frames_num), samples_num)
    cap = cv2.VideoCapture(filepath)
    for num in frames:
        cap.set(0, num)
        res, frame = cap.read()
        videoframes.append(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
    cap.release()
    del cap, num
    return videoframes

def resize_image(image, new_size):
    return cv2.resize(image, new_size, interpolation=cv2.INTER_AREA)

def crop_image(image):
    height, width, _ = image.shape
    max_x = height - 128
    max_y = width - 128
    rand_x = random.randint(0, max_x)
    rand_y = random.randint(0, max_y)
    return image[rand_x:(rand_x + 128), rand_y:(rand_y + 128), :]

def reading_annotations(videoname, dictionary):
    traits_list = ['extraversion', 'neuroticism', 'agreeableness', 'conscientiousness', 'openness']
    personal_traits = [float(dictionary[trait][videoname]) for trait in traits_list]
    return np.stack(personal_traits).reshape(5, 1)

def preprocess_data(audiopath, videopath, videoname, dictionary):
    preprocessed_audio = audio_preprocessing(audiopath)
    extracted_frames = extract_videoframes(filepath=videopath, samples_num=6)
    resized_images = [resize_image(image=frame, new_size=(248, 140)) for frame in extracted_frames]
    cropped_images = [crop_image(image=resized) / 255.0 for resized in resized_images]
    preprocessed_video = np.stack(cropped_images)
    annotations = reading_annotations(videoname=videoname, dictionary=dictionary)
    return preprocessed_audio, preprocessed_video, annotations

def reshape_to_expected_input(dataset: List[Tuple[np.ndarray, np.ndarray, np.ndarray]]) -> Tuple[
    np.ndarray, np.ndarray, np.ndarray]:
    x0_list = []
    x1_list = []
    y_list = []
    for i in range(0, len(dataset)):
        x0_list.append(dataset[i][0])
        x1_list.append(dataset[i][1])
        y_list.append(dataset[i][2])
    return (np.stack(x0_list), np.stack(x1_list), np.stack(y_list))
