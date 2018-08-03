# text2image
dependencies
- PIL


how to run
```
cd code
# for example, to create 1 image for tha+eng
python3 generate_data.py --num_instances 1 --langs tha+eng --num_sentences 2+2 \
      --text_source /data/DATA/ --font_dir ../thafonts ../engfonts
```
You can find more information by ```python3 generate_data.py -h```

The text_source is the W2C dataset, the txt files are too large. You may find it in M40 under /data/i351756/DATA

The code has only been tested for tha+eng, other languages require to add the fonts in this repo.
