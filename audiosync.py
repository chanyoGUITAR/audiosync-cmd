import librosa
import numpy as np
import os
import sys
from pydub import AudioSegment
import subprocess
import argparse
import tempfile


# Description: Computes a chromagram
# Input: numpy.ndarray (audio), sampling rate
# Return: numpy.ndarray (Normalized energy for each chroma bin at each frame)
# Uses: Librosa
def defineChromagram(audio, sr):
    chroma = librosa.feature.chroma_stft(y=audio, sr=sr, tuning=0, norm=2,
                                         hop_length=hop_size, n_fft=n_fft)
    return chroma


# Description: Runs .bat file to combine video and audio
# Input: Location of audio file, Location of Video File, Save Location ,audio begining sec, audio length(Sec)
# Return: None
# Uses: ffmpeg
def combine(audio_file, video_file, save_location, begin_sec, sec_main_audio):
    cmd = ['ffmpeg', '-y', 
            '-i', video_file,
            '-i', audio_file, 
            '-map', '0:v', 
            '-map', '1:a', 
            '-c:v', 'copy', 
            '-c:a', 'aac',
            '-ss', str(begin_sec), # 開始位置
            '-t', str(sec_main_audio),  # 長さ
            '-b:a', '160k', 
            save_location
           ]
    subprocess.run(cmd)


# Description: Runs .bat file to extract audio file from video
# Input: Location of Video File, Save Location
def extract(video_file, save_location):
    cmd = ['ffmpeg', '-y', '-loglevel', 'quiet', '-i', video_file, save_location]
    subprocess.run(cmd)


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Replaces the audio in a video file with '
                                                 'an external audio and maintains AV sync.')
    parser.add_argument('-v', '--video', help='path to video file', required=True, type=str)
    parser.add_argument('-ia', '--instaudio', help='path to inst audio file', required=True, type=str)
    parser.add_argument('-a', '--mainaudio', help='path to main audio file', required=True, type=str)
    parser.add_argument('-f', '--fft', default=1024, help='fft window size | recommended to be a power of 2 | default: 1024', required=False, type=int)
    parser.add_argument('-hl', '--hoplength', default=512, help='hop length | The number of samples between successive frames | default: 512', required=False, type=int)
    parser.add_argument('-sr', '--samplingrate', default=44100, help='sampling rate in Hz | Most applications use 44.1kHz | default: 44100 Hz', required=False, type=int)
    parser.add_argument('-d', '--duration', default=120, help='duration to check for offsets | default: 120 seconds', required=False, type=int)
    parser.add_argument('-o', '--output', help='export video file', required=True, type=str)

    args = parser.parse_args()
    if not os.path.exists(args.video):
        print('Video file does not exist.')
        sys.exit(-1)
    if not os.path.exists(args.mainaudio):
        print('Main Audio file does not exist.')
        sys.exit(-1)
    if not os.path.exists(args.instaudio):
        print('Inst Audio file does not exist.')
        sys.exit(-1)


# Vars
n_fft = args.fft # ftt window size
hop_size = args.hoplength # hop length
sampling_rate = args.samplingrate # sampling rate
duration_limit = args.duration # maximum duration of audio-video clips used to synchronize in seconds

audio_file = args.instaudio
main_audio_file = args.mainaudio
video_file = args.video

##############---------LOAD FILES---------##############

# Load audio file
audio, _ = librosa.load(audio_file, sr=sampling_rate, mono=True, duration=duration_limit)

# Load video file, creates .wav file of the video audio
handle, video_audio_file = tempfile.mkstemp(suffix='.wav')
os.close(handle)
extract(video_file, video_audio_file)
video, _ = librosa.load(video_audio_file, sr=sampling_rate, mono=True, duration=duration_limit)
os.unlink(video_audio_file)

##############---------RQA---------##############

# Chromagram
audio_chroma = defineChromagram(audio, sampling_rate)

# Chromagram
video_chroma = defineChromagram(video, sampling_rate)

# Performs RQA
xsim = librosa.segment.cross_similarity(audio_chroma, video_chroma, mode='affinity')
L_score, L_path = librosa.sequence.rqa(sim=xsim, gap_onset=np.inf, gap_extend=np.inf, backtrack=True)

audio_times = []
video_times = []
diff_times = []
for v, a in L_path * hop_size / sampling_rate:
    A = float(a)
    V = float(v)
    audio_times.append(A)
    video_times.append(V)
    diff_times.append((A - V))

##############---------SYNC PROCESS---------##############

# Find mean of time differences
diff_times = np.array(diff_times)
mean = np.average(diff_times)
std = np.std(diff_times)
diff_times = [d for d in diff_times if np.abs(d-mean) < (0.8*std)]
diff = np.average(diff_times)

# Setting move option
move = True if (diff > 0) else False

# Sync using PyDub
audio = AudioSegment.from_file(audio_file)
main_audio = AudioSegment.from_file(main_audio_file)
sec_main_audio = len(main_audio)/1000
begin_sec = abs(diff)

if move:
    # Trim diff seconds from beginning
    final = main_audio[diff * 1000:]
else:
    # Add diff seconds of silence to beginning
    silence = AudioSegment.silent(duration=-diff * 1000)
    final = silence + main_audio

# Export synced audio
handle, synced_audio = tempfile.mkstemp(suffix='.wav')
os.close(handle)
final.export(synced_audio, format='wav')

##############---------COMBINE PROCESS---------##############
save_file = args.output
combine(synced_audio, video_file, save_file, begin_sec, sec_main_audio)
os.unlink(synced_audio)
print('Synced and combined successfully to {}'.format(save_file))