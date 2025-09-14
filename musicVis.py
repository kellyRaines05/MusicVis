import librosa
import numpy as np
import pyaudio

def play_slowed_audio(input_file, rate):
    p = pyaudio.PyAudio()
    try:
        y, sr = librosa.load(input_file, sr=None)
        y_stretched = librosa.effects.time_stretch(y, rate=rate)
        y_int16 = (y_stretched * 32767).astype(np.int16)
        print("PLAYING SONG")
        stream = p.open(format=pyaudio.paInt16,
                    channels=1,
                    rate=sr,
                    output=True)
        
        stream.write(y_int16.tobytes())
        stream.stop_stream()
        stream.close()
        p.terminate()
    except FileNotFoundError:
        print(f"Error: The file {input_file} was not found.")
    except Exception as e:
        print(f"An error occurred: {e}")

input_audio = "C:/Users/kelly/Programming/Music-Synthesis/music_clips/s015.wav"
slow_down_rate = 0.97
play_slowed_audio(input_file=input_audio, rate=slow_down_rate)

# # use trained model generator
# music_file = ""
# model = ""
# model.predict(music_file)