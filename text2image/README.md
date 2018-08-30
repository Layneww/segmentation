# text2image
dependencies
- PIL

input needed
- fonts: .tff format, one folder per language.
- source text: under one folder, txt of each language should be named as `lang.txt`, where `lang` is the short form representation, such as thai-->tha, english-->eng, simplified chinese-->chi_sim. This notation should be consistant when defining the languages combination of the data creation to accurately locate the right text file.
Sample structure of a source text folder called DATA
```
DATA/
  eng.txt
  tha.txt
  chi_sim.txt
  ...
```

## structure of the dataset generated
default dataset folder is `/dataset`under the main repository. It stores the generated data.
Structure of the generated dataset folder
```
dataset/

  lang1+lang2/
  
    lang1+lang2.count.txt (created by generate_data.py file)
    
    train/
      decoder.txt ()
      image/
        0.jpg
        1.jpg
        ...
      xml/
        0.xml
        1.xml
        ...
      annotations/
        annotation_1000.csv
        annotation_2000.csv
        ...
      tfrecords/
        annotation_1000.tfrecords
        annotation_2000.tfrecords
        ...
    
    eval/
      (similar structure as the train/ folder)
```

## main functions
how to run
### generate image + .xml

```
cd code
# for example, to create 1 image for tha+eng
python3 generate_data.py --num_instances 1 --langs tha+eng --num_sentences 2+2 \
      --text_source /data/DATA/ --font_dir ../thafonts ../engfonts
```
You can find more information by `python3 generate_data.py -h`
```
  --langs LANGS         languages separated by +, e.g. tha+eng
  --num_sentences NUM_SENTENCES
                        number of sentences for each language separated by +,
                        e.g. 2+2
  --text_source TEXT_SOURCE
                        folder of the source txt, e.g. /data/DATA/
  --font_dir [FONT_DIR [FONT_DIR ...]]
                        font directoriess separated by ' ', e.g. thafontsdir engfontsdir
  --output_folder OUTPUT_FOLDER
                        output dataset folder path, defualt: '../dataset/'
  --num_instances NUM_INSTANCES
                        number of examples to generate
  --line_height LINE_HEIGHT
                        the height of one text line, default=32
  --pic_height PIC_HEIGHT
                        the height of the picture, default=600
  --pic_width PIC_WIDTH
                        the width of the picture, default=1000
  --font_size FONT_SIZE
                        the upper bound of font size, will be adjusted if the
                        font height is higher than the height of line
  --train TRAIN         a boolean value tells if creating training data, default:
                        True
  --max_char MAX_CHAR   the max number of characters for language text taken from 
                        one sentence
```

The text_source is the W2C dataset, the txt files are too large. You may find it in M40 under `/data/i351756/DATA`. You may also download partial text files from the release.

By default, by running the example code above, the images are created under `dataset/tha+eng/train/image` and the corresponding xml files are created under `dataset/tha+eng/train/xml`

The code has only been tested for combinations of the following 3 languages Thai,English and Chinese, other languages require to add the fonts in this repo but run in a similar way.

### convert .xml to annotation files (with threads)
```
python3 xml2csv.py --langs <languages>
```
You can specify the output folder, 
default it will generate the `annotation.csv` and `decoder.txt` under `../dataset/<languages>/train/`.

### a template to create customized tfrecords
```
python3 create_tfrecords.py --tfrecord <output tfrecord full path> --annotation <annotation.csv full path> --decoder <decoder.txt full path> --image_dir <image folder>
```
This template uses the same feature format as the French street model dataset [this paper](https://arxiv.org/abs/1702.03970) describes.

## other functions
### convert .tcc font file to .tff format
The `generate_data.py` only takes in .tff format as font source. Fonts with .tcc format need to be split into multiple .tff fonts.
The dependency is `fontforge`, which can only be used in python 2.X if install the prebuilt package in ubuntu.
```
# Install fontforge in ubuntu
sudo add-apt-repository ppa:fontforge/fontforge
sudo apt-get update
sudo apt-get install fontforge python-fontforge 
# run the function
python tcc2ttf.py <path of tcc file>
```
