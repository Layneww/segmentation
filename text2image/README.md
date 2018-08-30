# text2image
dependencies
- PIL

input needed
- source text: under one folder, txt of each language should be named as `lang.txt`, where `lang` is the short form representation, such as thai-->tha, english-->eng, simplified chinese-->chi_sim. This notation should be consistant when defining the languages combination of the data creation to accurately locate the right text file.
- fonts: .tff format, one folder per language.

## main functions
default dataset folder: `/dataset`under the main repository.
### generate image + .xml
how to run
```
cd code
# for example, to create 1 image for tha+eng
python3 generate_data.py --num_instances 1 --langs tha+eng --num_sentences 2+2 \
      --text_source /data/DATA/ --font_dir ../thafonts ../engfonts
```
You can find more information by `python3 generate_data.py -h`

The text_source is the W2C dataset, the txt files are too large. You may find it in M40 under `/data/i351756/DATA`

By default, by running the example code above, the images are created under `dataset/tha+eng/train/image` and the corresponding xml files are created under `dataset/tha+eng/train/xml`

The code has only been tested for combinations of the following 3 languages Thai,English and Chinese, other languages require to add the fonts in this repo but run in a similar way.

### convert .xml to annotation files (with threads)
```
python3 xml2csv.py --langs <languages>
```
You can specify the output folder, default it will generate the `annotation.csv` and `decoder.txt` under `../dataset/<languages>/train/`.
### a template to create customized tfrecords
```
python3 create_tfrecords.py --tfrecord <output tfrecord full path> --annotation <annotation.csv full path> --decoder <decoder.txt full path> --image_dir <image folder>
```
This template uses the same feature format as the [sequence model](https://github.wdf.sap.corp/I351756/sequence-model) does.

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
