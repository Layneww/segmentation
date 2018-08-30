# Multilingual Segmentation Model.

Refer to 
A TensorFlow implementation of the STREET model described in the paper:

"End-to-End Interpretation of the French Street Name Signs Dataset"

Available at: http://link.springer.com/chapter/10.1007%2F978-3-319-46604-0_30

The code has been mainly referred to the [STREET model](https://github.com/mldbai/tensorflow-models/tree/master/street).

## Contents
* [Introduction](#introduction)
* [Installing and setting up the segmentation model](#installing-and-setting-up-the-segmentation-model)
* [Create dataset](#create-dataset)
* [Training a full model with evaluation](#training-a-full-model-with-evaluation)
* [Inference on pixel level based (No visualization currently)](#inference-on-pixel-level-based-no-visualization-currently)
* [The Variable Graph Specification Language](#the-variable-graph-specification-language)

## Introduction

The model trains both Thai and English in one charset. The input is an textline image, and the output is a sequence of text.


## Installing and setting up the segmentation model

### Build from docker file. 
Create docker image from docerfile folder.
```
cd dockerfile
docker build -t <image name> .
```
Create container using 
```
nvidia-smi docker run -it -d --name <container name> -p 8888:8888 -p 6006:6006 -v <directory to be mapped>:<target mapped directory in docker> <image name>  /bin/bash
```

### Build some dependencies
tesseract 4.0 beta3. Refer to https://github.com/Layneww/Tesseract-Notes/blob/master/setupTesseract.md, Build Tesseract master branch from source. Please also build the training.

tesserocr: the python wrapper for tesseract. 
```
# go into the tesseract directory just git clone from github
cd tesseract
# include 'tesseract/osdetect.h' in library
cp src/ccmain/osdetect.h /usr/local/include/tesseract/
# install tesserocr
pip install tesserocr
```
pytesseract: another python wrapper
```pip install pytesseract```

### Build ops
Go into the directory of this project.
```
cd cc
TF_INC=$(python -c 'import tensorflow as tf; print(tf.sysconfig.get_include())')
TF_LIB=$(python -c 'import tensorflow as tf; print(tf.sysconfig.get_lib())')
g++ -std=c++11 -shared rnn_ops.cc -o rnn_ops.so -fPIC -I $TF_INC -O3 -mavx -D_GLIBCXX_USE_CXX11_ABI=0 -L $TF_LIB -ltensorflow_framework -O2
```
If appearing ```fatal error: nsync_cv.h: No such a file or directory```, add ```-I$TF_INC/external/nsync/public``` to the g++ command.
Refering to [TensorFlow Instruction](https://www.tensorflow.org/extend/adding_an_op#build_the_op_library) for more details.

Run the unittests:
```
cd python
python3 decoder_test.py
python3 errorcounter_test.py
python3 shapes_test.py
python3 vgslspecs_test.py
python3 vgsl_model_test.py
```

## Create dataset
Please refer to [text2image](../text2image/README.md)

## Training a full model with evaluation
The model structure is still under investigation.
Take tha+eng as an example.
```
cd python
# store model in 'model/' folder under 'segmentation-model/' direcotry
train_dir=../model
# rm -rf $train_dir  # uncomment this if want to retrain the whole model
CUDA_VISIBLE_DEVICES="0" python3 vgsl_train.py -model_str='1,32,0,1[Ct5,5,16 Mp3,3 Ct5,5,32 Mp3,3 DeCt5,5,32,3 DeCt3,3,16,3 Bl Lfys64 Lfx96 Lrx96 Lbx128]O1s3' --train_data=../dataset/tha+eng/train/tfrecords/* --train_dir=$train_dir --max_steps=1000000 &
CUDA_VISIBLE_DEVICES="" python3 vgsl_eval.py --model_str='1,32,0,1[Ct5,5,16 Mp3,3 Ct5,5,32 Mp3,3 DeCt5,5,32,3 DeCt3,3,16,3 Bl Lfys64 Lfx96 Lrx96 Lbx128]O1s3' --num_steps=1000 --eval_data=../dataset/tha+eng/eval/tfrecords/*  --decoder=../dataset/tha+eng/train/decoder.txt --eval_interval_secs=300 --train_dir=$train_dir --eval_dir=$train_dir/eval &
tensorboard --logdir=$train_dir
```

## Inference on pixel level based (No visualization currently)
To test the segmentation model. Suppose we have an image called `test.png` mixed with thai and english,
get the segmentation result on pixel
```
export PYTHONIOENCODING=UTF-8
train_dir=../model
python3 inference.py --train_dir=$train_dir --model_str='1,32,0,1[Ct5,5,16 Mp3,3 Ct5,5,32 Mp3,3 DeCt5,5,32,3 DeCt3,3,16,3 Bl Lfys64 Lfx96 Lrx96 Lbx128]O1s3' --image=test.png --decoder=../dataset/tha+eng/train/decoder.txt
```
The output will first print how many lines it finds during the preprocessing, and output the segmentation result.

## The Variable Graph Specification Language
Please see https://github.com/mldbai/tensorflow-models/blob/master/street/g3doc/vgslspecs.md for more details.
