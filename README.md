# segmentation-model
Language Detection and Segmentation model under progress. 
Include PIL based multilingual dataset generation. Take in text and font and output image with .xml annotation file

## text2image
Use the code in text2image to generate the multilingual dataset (tfrecords format) which will be used in the segmentation training.
Dataset is created in the `dataset/` folder under the main repo.
Structure of the tfrecords
```
dataset/

  lang1+lang2/
  
    lang1+lang2.count.txt
    
    train/
      decoder.txt
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

## segmentation-model
Please go into segmentation-model folder for detailed training and evaluation.
It uses the same code as the sequence-model to construct the network
TODO: convert the model network code to Keras.

