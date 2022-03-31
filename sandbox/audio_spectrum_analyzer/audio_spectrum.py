import pyaudio
import numpy
import matplotlib.pyplot as plt
import matplotlib.animation

RATE = 44100
BUFFER = 882

p = pyaudio.PyAudio()

stream = p.open(
    input_device_index= 2, # Select proper input device index <---------------------------- [!!!!!!!!!!!!!!!!!!!!]
    format = pyaudio.paFloat32,
    channels = 1,
    rate = RATE,
    input = True,
    output = False,
    frames_per_buffer = BUFFER
)

fig = plt.figure()
line1 = plt.plot([],[])[0]
line2 = plt.plot([],[])[0]

r = range(0,int(RATE/2+1),int(RATE/BUFFER))
l = len(r)

PRINT_BLUE_LINE = True
PRINT_SPECTRUM_LINE = True

# Tuning values
STARTING_VALUE = 0
SAMPLE = 5              # Higher - lower number of spectrum's, 1 sample = 50Hz
FADE_SPEED = 0.4        # Higher - faster fading



SAMPLE_AVERAGE = 0


def init_line():
    line1.set_data(r, [-1000] * l)
    line2.set_data(r, [-1000] * l)
    return line1, line2


def update_line(i):
    global SAMPLE_AVERAGE
    global STARTING_VALUE
    global SAMPLE

    try:
        b = numpy.fromstring(stream.read(BUFFER), dtype=numpy.float32)
        data = numpy.fft.rfft(b)
    except IOError:
        print('error')
        pass

    #data = numpy.log10(numpy.sqrt(numpy.real(data) ** 2 + numpy.imag(data) ** 2) / BUFFER) * 10
    data = data * -1

    if PRINT_BLUE_LINE:
        line1.set_data(r, data)
    else:
        line1.set_data(r, [0])

    test = numpy.maximum(data, line2.get_data())

    for i, point in enumerate(test[1]):
        # get SAMPLE_AVERAGE of first (STARTING_VALUE)..(SAMPLE) elements
        if i % SAMPLE == 0:
            SAMPLE_AVERAGE = 0
            sample_points = test[1][STARTING_VALUE:min((STARTING_VALUE + SAMPLE), len(test[1]) - 1)]
            for v in sample_points:
                if v > SAMPLE_AVERAGE:
                    SAMPLE_AVERAGE = v

            # replace SAMPLE_AVERAGE value for (STARTING_VALUE)..(SAMPLE) elements
            for index in range(STARTING_VALUE, min(STARTING_VALUE + SAMPLE, len(test[1]) - 1)):
                test[1][index] = SAMPLE_AVERAGE

            STARTING_VALUE += SAMPLE
            if STARTING_VALUE >= len(test[1]):
                STARTING_VALUE = 0

    for index in range(0, len(test[1]) - 1):
        if test[1][index] >= FADE_SPEED:
            if test[1][index] >= 70:
                test[1][index] = test[1][index] - (FADE_SPEED * 16)
            elif test[1][index] >= 60:
                test[1][index] = test[1][index] - (FADE_SPEED * 12)
            elif test[1][index] >= 50:
                test[1][index] = test[1][index] - (FADE_SPEED * 8)
            elif test[1][index] >= 40:
                test[1][index] = test[1][index] - (FADE_SPEED * 6)
            elif test[1][index] >= 30:
                test[1][index] = test[1][index] - (FADE_SPEED * 4)
            elif test[1][index] >= 20:
                test[1][index] = test[1][index] - (FADE_SPEED * 2)
            else:
                test[1][index] = test[1][index] - FADE_SPEED
        else:
            test[1][index] = 0

    if PRINT_SPECTRUM_LINE:
        line2.set_data(test)

    return line1, line2


plt.xlim([0, 14000])
plt.ylim(0, 70)
plt.xlabel('Frequency [Hz]')
plt.ylabel('dB')
plt.title('Spectrometer')
plt.grid()

line_ani = matplotlib.animation.FuncAnimation(
    fig, update_line, init_func=init_line, interval=0, blit=True
)

plt.show()