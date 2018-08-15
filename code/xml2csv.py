import os
import glob
import pandas as pd
import xml.etree.ElementTree as ET
import tensorflow as tf

tf.flags.DEFINE_string("langs",None, "languages, e.g. lang1+lang2")
tf.flags.DEFINE_string('data_dir', '../dataset', "full path of dataset folder")
tf.flags.DEFINE_float("train", True, "Train or Eval set")
tf.flags.DEFINE_string("output_dir", None, "output directory of the annotation.csv and decoder.txt")
FLAGS = tf.app.flags.FLAGS

decoder = ['<null>']
def xml_to_csv(path):
    print("extract annotation from", path)
    xml_list = []
    for xml_file in glob.glob(path + '/*.xml'):
        tree = ET.parse(xml_file)
        root = tree.getroot()
        for line in root.findall('line'):
            fname = root.find('filename').text
            filename = fname.split('.')[0]
            for seg in line.findall('object'):
                # check if it is new language
                if seg[0].text not in decoder:
                    decoder.append(seg[0].text)
                value = (filename,
                        int(line.find('bndbox')[0].text), # line xmin
                        int(line.find('bndbox')[1].text), # line xmax
                        int(line.find('bndbox')[2].text), # line ymin
                        int(line.find('bndbox')[3].text), # line ymax
                        seg[0].text,#decoder.index(seg[0].text), # language, encoded by number
                        int(seg[1][0].text), # seg xmin
                        int(seg[1][2].text), # seg xmax
                        )
                xml_list.append(value)
    column_name = ['ImageName', 'line_xmin', 'line_xmax','line_ymin','line_ymax', 'language', 'xmin', 'xmax']
    xml_df = pd.DataFrame(xml_list, columns=column_name)
    return xml_df

def to_decoder(decoder_path, decoder=decoder):
    with open(decoder_path, 'w', encoding='utf-8') as f:
        for i, e in enumerate(decoder):
           f.write("{}\t{}\n".format(e, i)) 

def main():
    assert FLAGS.data_dir, 'Root directory of dataset folder does not exist'
    dataset_type = 'train'
    if not FLAGS.train:
        dataset_type = 'eval'
    data_dir = os.path.join(FLAGS.data_dir, FLAGS.langs, dataset_type)
    xml_path = os.path.join(data_dir, 'xml')
    xml_df = xml_to_csv(xml_path)
    output_dir = FLAGS.output_dir
    output_path = 'annotations.csv'
    if not output_dir:
        output_dir = data_dir
    xml_df.to_csv(os.path.join(output_dir, 'annotations.csv'), index=None)
    print('Successfully converted xml to csv.')
    to_decoder(os.path.join(output_dir, 'decoder.txt'))
    print('Successfully generate decoder.')

if __name__ == '__main__':
    main()
