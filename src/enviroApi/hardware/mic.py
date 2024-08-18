
if enable_noise:
    import sounddevice as sd
    import numpy as np
    from numpy import pi, log10
    from scipy.signal import zpk2tf, zpk2sos, freqs, sosfilt
    from waveform_analysis.weighting_filters._filter_design import _zpkbilinear