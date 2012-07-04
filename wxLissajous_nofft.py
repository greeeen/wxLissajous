#!/usr/local/bin/python
# -*- coding: utf-8 -*-
'''wxLissajous
original: .../pyAudio/test_LR_lissajous.py
          ( Reference - http://d.hatena.ne.jp/aidiary/20110716/1310824587 )
data: The "Hatsune Miku's negi up down data" is wave audio captured
      from http://www.nicovideo.jp/watch/sm5277506/ , so many thanks.
'''

import sys, os
import wave
import pyaudio
import numpy as np
import matplotlib
matplotlib.use('WXAgg')
import matplotlib.pyplot as plt
import wx

usetimer = False # True
filename = 'data/sm5277506_short.wav' # 2 (LR) channel * 2 ('int16') bytes

wf = wave.open(filename, 'rb')
fs = wf.getframerate() # sampling frequency
nb = wf.getnchannels() * wf.getsampwidth() # 2(LR) * 2bytes
buf = wf.readframes(wf.getnframes())
pa = pyaudio.PyAudio()
stream = pa.open(format=pa.get_format_from_width(wf.getsampwidth()),
  channels=wf.getnchannels(), rate=wf.getframerate(), output=True)
wf.close()

fig = plt.figure()
sp0 = fig.add_subplot(222)
sp1 = fig.add_subplot(221)
sp2 = fig.add_subplot(224)
sp3 = fig.add_subplot(223)

d = np.frombuffer(buf, dtype='int16')
e = d / (5.0 * 32768.0) # autoscale off and regulation -1.0 <-> +1.0
l = e[0::2] # Left channel
r = e[1::2] # Right channel
s = len(l)
print len(d)

start = 1500000 # 0        # sampling start position
N = 3072 # 1792 # 512      # number of FFT samples
SHIFT = 1024    # 128      # number of windowfunc shift samples

hammingWindow = np.hamming(N)
F = np.fft.fftfreq(N, d=1.0/fs)

inbuffered = False

def buffered(idleevent):
  global inbuffered
  if inbuffered: return
  inbuffered = True
  wx.CallLater(2, update, idleevent)

def update(idleevent):
  global inbuffered, start
  #stream.write(np.array(d[start*2:(start+SHIFT)*2], dtype='int16').tostring())
  stream.write(buf[start*nb:(start+SHIFT)*nb])
  x, y = r[start:start+N], l[start:start+N]

  sp0.cla()
  sp0.plot(x, y, 'g')
  sp0.axis([-0.3, 0.3, -0.3, 0.3])
  sp0.set_xlabel('x')
  sp0.set_ylabel('y')

  '''
  sp1.cla()
  sp1.plot(xrange(start, start+N), y, 'b')
  sp1.axis([start, start+N, -0.3, 0.3])
  sp1.set_xlabel('time [sample]')
  sp1.set_ylabel('amplitude')

  sp2.cla()
  sp2.plot(x, xrange(start, start+N), 'b')
  sp2.axis([-0.3, 0.3, start, start+N])
  sp2.set_xlabel('amplitude')
  sp2.set_ylabel('time [sample]')

  Z = np.fft.fft(hammingWindow * (x + y))
  amplitudeSpectrum = [np.sqrt(c.real ** 2 + c.imag ** 2) for c in Z]
  sp3.cla()
  sp3.plot(F, amplitudeSpectrum, 'ro', markersize=2, linestyle='-')
  # sp3.axis([0, fs/2, 0, 20])
  sp3.axis([0, 2000, 0, 100])
  sp3.set_xlabel('frequency [Hz]')
  sp3.set_ylabel('amplitude spectrum')
  '''

  fig.canvas.draw_idle()
  start += SHIFT
  inbuffered = False
  if not usetimer: idleevent.RequestMore(needMore=True)
  if start + N > s:
    stream.close()
    pa.terminate()
    sys.exit()

if usetimer:
  timer = wx.Timer(wx.GetApp(), id=1)
  timer.Start(1)
  wx.EVT_TIMER(wx.GetApp(), 1, buffered)
else:
  wx.EVT_IDLE(wx.GetApp(), buffered)
plt.show()
