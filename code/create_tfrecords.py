import os
import math
import sys
import numpy as np
import cv2
import tensorflow as tf
import glob
import pandas as pd


flags = tf.app.flags
flags.DEFINE_string('tfrecord', 'dataset.tfrecords', 'the path to the output tfrecord')
flags.DEFINE_string('annotation', 'annotations.csv', 'the path to the annotation file')
flags.DEFINE_string('decoder', 'decoder.txt', 'the path to the decoder file')
flags.DEFINE_string('image_dir', 'image', 'the path to the directory of all images')

FLAGS = flags.FLAGS

HEIGHT=32

def df2list(xml_df):
    example_list = []
    # image_name, xmin, ymin, height, width, label
    line = {}
    cur_image, cur_ymin, cur_xmax = [None]*3
    for index, seg in xml_df.iterrows():
        image_name, line_xmin, line_ymin, line_xmax, line_ymax, language, xmin, xmax = seg
        # check if is next line
        if not (cur_image == image_name and cur_ymin == line_ymin):
            # add more nulls at end if any
            if index != 0:
                while len(line['label']) < line['width']:
                    line['label'].append('<null>') 
                # add to example list
                example_list.append(line)
            # reset
            line = {'image_name':image_name, 'xmin':line_xmin, 'ymin':line_ymin, 
                    'height':line_ymax-line_ymin, 'width':line_xmax-line_xmin, 'label':[]}
            cur_image = image_name
            cur_ymin = line_ymin
            cur_xmax = line_xmin
        # continue adding line info
        # add null label
        while cur_xmax < xmin:
            line['label'].append('<null>') 
            cur_xmax += 1
        # add language label
        while cur_xmax < xmax:
            line['label'].append(language)
            cur_xmax += 1
    # add last line
    while len(line['label']) < line['width']:
        line['label'].append('<null>') 
    # add to example list
    example_list.append(line) 
    return example_list

# decoder
def get_encoder(decoder_path):
    encoder = {}
    for a in open(decoder_path, 'r').readlines():
        pair = a.split('\t')
        encoder[pair[0]] = int(pair[1])
    return encoder

# write to tfrecord
def create_tfrecord(tfrecords_filename, annotation_path, decoder_path, image_folder):
    xml_df = pd.read_csv(annotation_path)
    example_list = df2list(xml_df)
    writer = tf.python_io.TFRecordWriter(tfrecords_filename)
    for line in example_list:
        image_path = os.path.join(image_folder, str(line['image_name'])+'.jpg')
        crop_window = [line['ymin'], line['xmin'], line['height'], line['width']]
        line_encoded = crop_jpeg_and_encode(image_path, crop_window)
        with tf.Session() as sess:
            line_string = line_encoded.eval()
        decoder = get_encoder(decoder_path)
        example = tf.train.Example(features=tf.train.Features(
                feature={
                    'image/format': _bytes_feature(tf.compat.as_bytes('JPEG')),   
                    'image/encoded': _bytes_feature(line_string),
                    'image/class': _int64_list_feature([decoder[x] for x in line['label']]),
                    'image/unpadded_class': _int64_list_feature([decoder[x] for x in line['label']]),
                    'image/width': _int64_feature(int(HEIGHT/crop_window[2]*crop_window[3])),
                    'image/height': _int64_feature(HEIGHT),
                    'image/text': _bytes_feature(tf.compat.as_bytes(''.join(line['label'])))
                }))
        writer.write(example.SerializeToString()) 

# helper function
def _int64_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=[value]))

def _int64_list_feature(value):
    return tf.train.Feature(int64_list=tf.train.Int64List(value=value))

def _bytes_feature(value):
    return tf.train.Feature(bytes_list=tf.train.BytesList(value=[value]))

def crop_jpeg_and_encode(image_path, crop_window):
    with tf.gfile.GFile(image_path, 'rb') as fid:
        encoded_jpg = fid.read()
    decoded_crop = tf.image.decode_and_crop_jpeg(encoded_jpg, crop_window=crop_window)
    resize_crop = tf.image.resize_images(decoded_crop, size=[32, int(32/crop_window[2]*crop_window[3])], method=tf.image.ResizeMethod.BILINEAR)
    decoded_crop = tf.cast(resize_crop, tf.uint8)
    encoded_crop = tf.image.encode_jpeg(decoded_crop, quality=100)
#     print('crop_window', crop_window)
#     with tf.Session() as sess:
#         print(decoded_crop.eval().shape)
#         import matplotlib.pyplot as plt
#         plt.imshow(decoded_crop.eval())
#         plt.show()
    return encoded_crop

def main():
    image_folder = FLAGS.image_dir
    create_tfrecord(FLAGS.tfrecord, FLAGS.annotation, FLAGS.decoder, image_folder)


if __name__ == '__main__':
    main()
