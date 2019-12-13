from scipy import roll
from scipy.signal import butter, sosfilt, welch, firwin, lfilter
import numpy as np
from sklearn import preprocessing
# from APP import ArdSerial
from scipy.fftpack import fft
from entropy.entropy import *
import time
import pywt


# def update_screen(current_plot, win_size, fft_b=False):
#     plot = current_plot
#     plot = roll(plot, - win_size)
#     plot[- win_size:] = ArdSerial.get_chunk(win_size)
#     return plot


def get_fft(signal, fs):
    # Number of sample points
    n = len(signal)
    # sample spacing
    t = 1.0 / fs
    x = np.linspace(0.0, n * t, n)
    yf = fft(signal)
    signal_fft = 2.0 / n * np.abs(yf[0:n // 2])
    xf = np.linspace(0.0, 1.0 / (2.0 * t), n // 2)
    return xf, signal_fft


def get_psd(signal, fs):
    f, pxx_den = welch(signal, fs)  # , nperseg=1024
    return f, pxx_den


def scaling_data(signal):
    scaled = np.interp(signal, (0.0, 1000.0), (-1, +1))
    return scaled


def waveletdec(signal):
    dec_wave_lvs = pywt.wavedec(signal, 'coif1', level=2)
    dec_wave = dec_wave_lvs[0]
    return dec_wave


def featuresExtract(signal):
    Ent = spectral_entropy(signal, 100, method='welch', normalize=True)
    N5 = np.nanpercentile(signal, 5)
    Std = np.nanstd(signal)
    Var = np.nanvar(signal)
    NEnt = norm_entropy(signal)
    Mean = SRAV(signal)
    return Ent, N5, Std, Var, NEnt, Mean


def SRAV(x):
    SRA = sum(np.sqrt(abs(x)))
    return np.power(SRA / len(x), 2)


def norm_entropy(x):
    tresh = 2
    return sum(np.power(abs(x), tresh))


#################### Filter IIR #####################
def get_high_pass_IIR(sig, fc, fs, order):
    sos = butter(order, fc, 'hp', fs=fs, output='sos')
    filtered = sosfilt(sos, sig)
    return filtered


def get_low_pass_IIR(sig, fc, fs, order):
    #    start_time = time.time()
    sos = butter(order, fc, 'low', fs=fs, output='sos')
    filtered = sosfilt(sos, sig)
    #    print("--- %s seconds ---" % (time.time() - start_time))
    return filtered


def get_band_pass_IIR(sig, lc, hc, fs, order):
    sos = butter(order, [lc, hc], 'bandpass', fs=fs, output='sos')
    filtered = sosfilt(sos, sig)
    return filtered


def get_band_stop_IIR(sig, lc, hc, fs, order):
    sos = butter(order, [lc, hc], 'bandstop', fs=fs, output='sos')
    filtered = sosfilt(sos, sig)
    return filtered


#################### Filter FIR #####################
def get_high_pass_FIR(sig, fc, fs, order=11):
    nyq_rate = fs / 2.0
    f1 = fc / nyq_rate
    b = firwin(order, f1, pass_zero='highpass')
    filtered = lfilter(b, 1, sig)
    return filtered


def get_low_pass_FIR(sig, fc, fs, order=11):
    nyq_rate = fs / 2.0
    f1 = fc / nyq_rate
    b = firwin(order, f1, pass_zero='lowpass')
    filtered = lfilter(b, 1, sig)
    return filtered


def get_band_pass_FIR(sig, lc, hc, fs, order=11):
    nyq_rate = fs / 2.0
    f1 = lc / nyq_rate
    f2 = hc / nyq_rate
    b = firwin(order, [f1, f2], pass_zero='bandpass')
    filtered = lfilter(b, 1, sig)
    return filtered


def get_band_stop_FIR(sig, lc, hc, fs, order=101):
    nyq_rate = fs / 2.0
    f1 = lc / nyq_rate
    f2 = hc / nyq_rate
    b = firwin(order, [f1, f2], pass_zero='bandstop')
    filtered = lfilter(b, 1, sig)
    return filtered


############### Pipeline ###################

def pipeLine_screen(signal, lc, hc, fs):
    scaled = scaling_data(signal)
    bandPassed = get_band_pass_FIR(scaled, lc, hc, fs)
    # bandPassed = get_band_stop_FIR(bandPassed, 50, 70, fs, order=101)
    return bandPassed


def pipeLine_fDomain(signal, lc, hc, fs):
    pipe = pipeLine_screen(signal, lc, hc, fs)
    fft = get_fft(signal, fs)
    return fft
