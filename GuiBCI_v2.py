import sys
import serial
from scipy import roll
from scipy.signal import welch
from pyqtgraph.Qt import QtGui, QtCore
import pyqtgraph as pg
import pyqtgraph.widgets.RemoteGraphicsView
import numpy as np
import dataProcessing as dp
from joblib import load


class PlotEEG(object):
    def __init__(self):
        BAUDE_RATE = 9600
        COM = 'COM5'
        self.WINDOW_SIZE = 4
        self.MAX_DATA_SIZE = 1024
        self.FS = 190
        self.MODEL = load('Eyes_Op_Cl_MLP_89.1%.joblib')
        self.app = pg.mkQApp()


        # view 1
        self.view = pg.widgets.RemoteGraphicsView.RemoteGraphicsView()
        self.view.setWindowTitle('Classe: RemoteSpeedTest')
        pg.setConfigOptions(antialias=True)
        self.view.pg.setConfigOptions(antialias=True)  ## prettier plots at no cost to the main process!
        self.view.setWindowTitle('pyqtgraph example: RemoteSpeedTest')


        # view 2
        self.view2 = pg.widgets.RemoteGraphicsView.RemoteGraphicsView()
        self.view2.setWindowTitle('Classe: RemoteSpeedTest')
        pg.setConfigOptions(antialias=True)
        self.view2.pg.setConfigOptions(antialias=True)  ## prettier plots at no cost to the main process!
        self.view2.setWindowTitle('FFT')

        self.label = QtGui.QLabel()
        # Check Boxes
        self.check_clf = QtGui.QCheckBox('Classificar')
        self.check_rcd = QtGui.QCheckBox('Gravar')
        self.check_HPF = QtGui.QCheckBox('High Pass Filter')
        self.check_LPF = QtGui.QCheckBox('Low Pass Filter')
        self.check_BPF = QtGui.QCheckBox('Band Pass Filter')

        # Adding layout and wodgets
        self.layout = pg.LayoutWidget()
        self.layout.addWidget(self.check_rcd)
        self.layout.addWidget(self.check_clf)
        self.layout.addWidget(self.label)
        self.layout.addWidget(self.view, row=1, col=0,colspan=3 )
        self.layout.addWidget(self.view2, row=2, col=0, colspan=3)
        self.layout.addWidget(self.check_HPF, row=3, col=0)
        self.layout.addWidget(self.check_LPF, row=3, col=1)
        self.layout.addWidget(self.check_BPF, row=3, col=2)

        # Adding Plots

        self.layout.resize(800, 800)
        self.layout.show()

        # Setup plot wave
        self.wave_plot = self.view.pg.PlotItem()
        self.wave_plot._setProxyOptions(deferGetattr=True)
        self.view.setCentralItem(self.wave_plot)

        # Setup plot fft
        self.spectro_plot = self.view2.pg.PlotItem()
        self.spectro_plot._setProxyOptions(deferGetattr=True)
        self.view2.setCentralItem(self.spectro_plot)

        # Computting FPS
        self.lastUpdate = pg.ptime.time()
        self.avgFps = 0.0

        # Plot lines
        self.buffer = np.zeros(1024)
        self.wave_plot.plot(self.buffer, clear=True)
        self.label.setText(
            "<span style='font-size: 20pt'><span style='color: green'>Classe: ___ fps</span>")

        # Serial config
        self.ser = serial.Serial(COM, BAUDE_RATE)
        self.lstUpClf = 0


        # Gravar
        self.file = []

    def update_wav(audio):
        numpy_data = numpy.array(audio, dtype=float)
        scipy.io.wavfile.write("test.wav", 8000, numpy_data)

    def start(self):
        if (sys.flags.interactive != 1) or not hasattr(QtCore, 'PYQT_VERSION'):
            QtGui.QApplication.instance().exec_()

    def update(self):
        chunk = []
        for x in range(self.WINDOW_SIZE):
            r = float(self.ser.readline())
            r = dp.scaling_data(r)
            chunk.append(r)

        self.buffer = roll(self.buffer, - self.WINDOW_SIZE)
        self.buffer[- self.WINDOW_SIZE:] = chunk


        # Filters
        if self.check_HPF.isChecked():
            self.buffer = dp.get_high_pass_FIR(self.buffer, 2, self.FS, order=5)

        if self.check_LPF.isChecked():
            aux = self.buffer[:-100]
            aux = dp.get_low_pass_IIR(aux, 40, self.FS, order=5)
            self.buffer[:-100] = aux

        if self.check_BPF.isChecked():
            self.buffer = dp.get_band_pass_IIR(self.buffer, 2, 50, self.FS, order=5)



        # eixo, power_spectrum = dp.get_psd(self.buffer, self.FS)
        f, pxx_den = welch(self.buffer[-200:], self.FS)

        self.wave_plot.plot(self.buffer[:], clear=True, pen=(0, 255, 0), _callSync='off')
        self.spectro_plot.plot(x=f, y=pxx_den, clear=True, pen=(0, 100, 255), _callSync='off')

        # Fps Handling
        now = pg.ptime.time()
        fps = 1.0 / (now - self.lastUpdate)
        self.lastUpdate = now
        self.avgFps = self.avgFps * 0.8 + fps * 0.2

        # Classificar Sinal
        if self.check_clf.isChecked():
            if (pg.ptime.time() - self.lstUpClf) >= 2:
                g = dp.featuresExtract(dp.waveletdec(self.buffer[-200:]))
                result = self.MODEL.predict(np.array(g).reshape(-1, 6))
                cp = 'Olho Fechado' if result == 0 else 'Olho Aberto'
                self.label.setText(
                    "<span style='font-size: 20pt'><span style='color: green'>Classe: %s </span>" % cp)
                self.lstUpClf = pg.ptime.time()

        # Gravar sinal
        if self.check_rcd.isChecked():
            self.file.extend(chunk)

    def animation(self):
        timer = QtCore.QTimer()
        timer.timeout.connect(self.update)
        timer.start()
        self.start()


if __name__ == '__main__':
    p = PlotEEG()
    p.animation()
