'''
References:

https://stackoverflow.com/questions/8299303/generating-sine-wave-sound-in-python
https://github.com/danilobellini/audiolazy/blob/master/examples/shepard.py
https://en.wikipedia.org/wiki/Shepard_tone
https://medium.com/@cambridgecodingacademy/programming-challenge-shepard-tone-in-sonic-pi-eee46e91f0bb

'''
import pyaudio
import numpy as np


def genSine(A, f, phi, fs, t):
	"""
	Inputs:
		A (float) = amplitude of the sinusoid
		f (float) = frequency of the sinusoid
		phi (float) = initial phase of the sinusoid
		fs (float) = sampling frequency of the sinusoid
		t (float) = duration of the sinusoid (in seconds)
	Output:
		x = (numpy array) = The generated sinusoid
	"""

	t = np.arange(0, t, 1.0/fs)
	x = A * np.cos(2 * np.pi * f * t + phi)

	return x

def genChirp(A, fs, t, f0, t1, f1, phi=0):
	"""
	Reference:

	https://scipy-cookbook.readthedocs.io/items/FrequencySweptDemo.html
	https://github.com/scipy/scipy/blob/v1.4.1/scipy/signal/waveforms.py#L265-L430
	"""
	t = np.arange(0, t, 1.0/fs)
	beta = (f1 - f0) / t1
	phase = 2 * np.pi * (f0 * t + beta * t * t)

	phi *= np.pi / 180
	return A * np.cos(phase + phi)

def fadeInFadeOutRamp(amplitude, duration, fs):
	"""
	This is super hacky :(
	"""
	fadeIn = np.linspace(0, amplitude, int(duration) * fs // 2)
	fadeOut = np.linspace(amplitude, 0, int(duration) * fs // 2)
	return np.concatenate((fadeIn, fadeOut))

p = pyaudio.PyAudio()

amplitude = 0.7
fs = 44100
duration = 10.0
sine_freq = 367.0 
chirp_start_freq = 440.0
chirp_end_freq = 880.0

chirp = genChirp(amplitude, fs, duration, chirp_start_freq, duration, chirp_end_freq).astype(np.float32)
fade_ramp = fadeInFadeOutRamp(amplitude, duration, fs)

fadeInFadeOutChirp1 = (chirp * fade_ramp).astype(np.float32)#.tobytes()
fadeInFadeOutChirp2 = (chirp * fade_ramp).astype(np.float32)#.tobytes()

final_chirp = np.arange(0, 20, 1/fs)

final_chirp[0:10*fs] = fadeInFadeOutChirp1
added_section = np.add(final_chirp[5*fs:15*fs], fadeInFadeOutChirp2)
final_chirp[5*fs:15*fs] = added_section
final_chirp = final_chirp.astype(np.float32).tobytes()

# sine_wav = genSine(amplitude, sine_freq, 0, fs, duration).astype(np.float32).tobytes()  # need this to be floats or you're going to get a nice high amplitude square wave to your brain :)

stream = p.open(
	format=pyaudio.paFloat32,
	channels=1,
	rate=fs,
	output=True
	)

stream.write(final_chirp)

stream.stop_stream()
stream.close()

p.terminate()
