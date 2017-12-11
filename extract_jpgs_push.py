# coding: utf-8
import argparse, os, sys
import tensorflow as tf
import StringIO
from  PIL import Image

parser = argparse.ArgumentParser()
parser.add_argument('tfrpath', type=str,
                    help='path to tfrecords')
parser.add_argument('jpgspath', type=str,
                    help='path where to dump all the jpgs')
parser.add_argument('--file-prefix', type=str, default='push-jpgs',
                    help='prefix of file for all processed examples')
args = parser.parse_args()

tfr_dir = os.path.abspath(args.tfrpath)
os.makedirs(args.jpgspath)
out_dir = os.path.abspath(args.jpgspath)

# use this script first to hate dataset release in tfrecords
# second to extract jpegs out of them
# the main problem is that we don't know the feature field of every timesteps per example
# which is held in 'move/N/image/encoded'. N has a diff max value depending on the example.

# This script will first loop over that feature field until the serialized jpeg to a string is empty.
# Second, it will loop into the Feature classes fields until we finally get our real jpeg string.
# Somehow, our jpeg string is buried deep in a hierarchy of google what not proto buffer class.
# Could be a better way???!!! tfrecords doc == crap.

i = 0
for tfrecord in os.listdir(tfr_dir):
    print "Processing tfrecord", tfrecord
    for tfrecord_iterated in tf.python_io.tf_record_iterator(os.path.join(tfr_dir, tfrecord)):
        this_exp_dir = os.path.join(out_dir, args.file_prefix + '-' + str(i))
        os.makedirs(this_exp_dir)
        print
        print "Example", i
        example = tf.train.Example.FromString(tfrecord_iterated)
        j = 0
        while len(example.features.feature['move/{}/image/encoded'.format(j)].SerializeToString()) > 0:
            jpg_as_str = example.features.feature['move/{}/image/encoded'.format(j)]
            sys.stdout.write('\rjpeging %d'%(j))
            sys.stdout.flush()
            # go as deep as we can in this forsaken structure so we get our jpg
            while hasattr(jpg_as_str, 'ListFields'):
                jpg_as_str = jpg_as_str.ListFields()[0][1]

            img = Image.open(StringIO.StringIO(jpg_as_str[0]))
            img.save(os.path.join(this_exp_dir, 'image-{}.jpg'.format(j)), "JPEG")
            j += 1
        i += 1
