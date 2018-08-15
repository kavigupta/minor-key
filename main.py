
import argparse

import numpy as np
from scipy.io import wavfile as wav

from minor_key import minor_key, minor_to_major, major_to_minor

parser = argparse.ArgumentParser(description='Convert song from major to minor key')

parser.add_argument('--input-file')
parser.add_argument('--output-file', default=None)
parser.add_argument('--translation-policy',
                    help='typically minor_to_major, major_to_minor(harmonic=?)')
parser.add_argument('--number-notes',
                    type=int,
                    default=4,
                    help='number of notes to use in key identification')
parser.add_argument('--number-keys',
                    type=int,
                    default=1,
                    help='number of keys expected in this song')
parser.add_argument('--chunk-size',
                    type=int,
                    default=1000,
                    help='size of chunks used in key identification and song transformation (ms)')

args = parser.parse_args()

output_file = args.output_file or args.input_file[:-len(".wav")] + "-result.wav"

rate, data = wav.read(args.input_file)

def proc_channel(channel):
    return minor_key(
        channel,
        rate,
        eval(args.translation_policy, dict(major_to_minor=major_to_minor, minor_to_major=minor_to_major)),
        number_notes=args.number_notes,
        number_keys=args.number_keys,
        chunk_size=args.chunk_size / 1000)

if len(data.shape) == 1:
    result = proc_channel(data)
elif len(data.shape) == 2:
    assert data.shape[1] == 2
    result = np.array([proc_channel(data[:,idx]) for idx in range(2)]).T
else:
    raise RuntimeError("Weird wav format: shape is {}".format(data.shape))

wav.write(output_file, rate, result)
