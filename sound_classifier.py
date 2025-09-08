import crepe
import numpy as np
import time
import socket
from scipy.io import wavfile
from pythonosc import udp_client

training_folder = "c:/Users/18155/Programming/nsynth_dataset/nsynth-train/audio"
validation_folder = "c:/Users/18155/Programming/nsynth_dataset/nsynth-valid/audio"
testing_folder = "c:/Users/18155/Programming/nsynth_dataset/nsynth-test/audio"

instrument_sources = [0, 1, 2] # acoustic, electric, synthetic
instrument_families = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10]  # bass, brass, flute, guitar, keyboard, mallet, organ, reed, string, synth_lead, vocal
note_qualities = [0, 1, 2, 3, 4, 5, 6, 7, 8, 9] # bright, dark, distortion, fast_decay, long_release, multiphonic, nonlinear_env, percussive, reverb, tempo-synced

def detect_pitch(file):
    sr, audio = wavfile.read(file)
    _, frequency, _, _ = crepe.predict(audio, sr, model_capacity="medium", step_size=150, viterbi=True, )
    midi = 69 + 12 * np.log2(frequency / 440.0)
    notes = np.rint(midi).astype(int)
    notes = np.unique(notes)
    return notes

val = 0
def detect_velocity(file):
    client = udp_client.SimpleUDPClient("127.0.0.1", 5006)
    client.send_message("/file", file)

start = time.time()
print(detect_velocity("c:/Users/18155/Programming/nsynth_dataset/nsynth-train/audio/bass_acoustic_000-045-127.wav"))
print(time.time() - start)