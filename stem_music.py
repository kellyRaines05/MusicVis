import demucs.separate
import shlex
from pydub import AudioSegment, silence
import time

model = "htdemucs_ft"

def stem_song(file):
    demucs.separate.main(shlex.split(f'-n {model} {file}'))
    output = file.split("/")
    return f"separated/{model}/{output[len(output) - 1]}"

def detect_silence(file):
    myaudio = AudioSegment.from_wav(file)
    silence_times = silence.detect_silence(myaudio, min_silence_len=1000, silence_thresh=-25)

    if len(silence_times) == 1 and silence_times[0][1] == len(myaudio):
        print(silence_times)
        return True
    else:
        print(silence_times)
        return False

start = time.time()
stem_song("C:/Users/18155/Programming/MusicVis/all_data/music_clips/s003.wav")
end = time.time()
print("Time taken:", end - start)