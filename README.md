# text2image
Tesseract's function which takes one text file and one font to generate the image and box file

## general usage
To find available fonts in a specific fonts_dir
```
text2image --list_available_fonts --fonts_dir <the desired directory, e.g. /usr/share/fonts>
```
To generate the tif/box pair, run:
```
text2image --fonts_dir=/usr/share/fonts --text=training_text.txt --outputbase=[lang].[fontname].exp0 --font='Font Name' 
```

To list all fonts in your system which can render the training text, run:
```
text2image --text=training_text.txt --outputbase=eng --fonts_dir=/usr/share/fonts  --find_fonts --min_coverage=1.0 --render_per_font=false
```
## Note
There are a lot of header files that this program depends on. Please check in the cpp file.
My suggestion is to install all the libraries and build tesseract from source...

