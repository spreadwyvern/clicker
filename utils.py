import math

from pyaudio import PyAudio # sudo apt-get install python{,3}-pyaudio
from winsound import PlaySound, SND_FILENAME, SND_LOOP, SND_ASYNC


try:
    from itertools import izip
except ImportError: # Python 3
    izip = zip
    xrange = range

def main():
    print('play sound')
    PlaySound('iso8201_lf.wav', SND_FILENAME|SND_LOOP)
    # sine_tone(
    # # see http://www.phy.mtu.edu/~suits/notefreqs.html
    # frequency=420.00, # Hz, waves per second A4
    # duration=0.1, # seconds to play sound
    # interval = 0.1,
    # sounds = 3,
    # volume=.1, # 0..1 how loud it is
    # # see http://en.wikipedia.org/wiki/Bit_rate#Audio
    # sample_rate=22050 # number of samples per second
    # )

def sine_tone(frequency, duration, interval, sounds, volume=1, sample_rate=22050):
    n_samples = int(sample_rate * duration)
    restframes = n_samples % sample_rate

    p = PyAudio()
    stream = p.open(format=p.get_format_from_width(1), # 8bit
                    channels=1, # mono
                    rate=sample_rate,
                    output=True)
    s = lambda t: volume * math.sin(2 * math.pi * frequency * t / sample_rate)
    # samples = (int(s(t) * 0x7f + 0x80) for t in xrange(n_samples))
    # for buf in izip(*[samples]*sample_rate): # write several samples at a time
    #     stream.write(bytes(bytearray(buf)))
    # samples = []
    # for n in range(sounds):
    samples = (int(s(t) * 0x7f + 0x80) for t in range(n_samples))
    samples = bytes(bytearray(samples))

    sound = samples
    for n in range(sounds-1):
        sound += b'\x80' * int(interval * sample_rate) + samples
    # samples = samples + b'\x80' * int(interval * sample_rate) + samples
    # stream.write(bytes(bytearray(samples)))
    stream.write(sound)
    # fill remainder of frameset with silence
    stream.write(b'\x80' * restframes)

    stream.stop_stream()
    stream.close()
    p.terminate()

def play_sound():
    PlaySound('iso8201_lf.wav', SND_FILENAME|SND_LOOP)

def stop_sound():
    PlaySound(None, SND_FILENAME)

if __name__ == '__main__':
    main()