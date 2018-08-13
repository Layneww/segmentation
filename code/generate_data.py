from random import shuffle
import random
from PIL import ImageDraw
from PIL import ImageFont
from PIL import Image
import os
import linecache
import glob

from xml.etree.ElementTree import Element, SubElement, Comment, tostring
from xml.etree import ElementTree
from xml.dom import minidom
import xml.etree.cElementTree as ET


import os
os.environ["CUDA_DEVICE_ORDER"] = "PCI_BUS_ID"
os.environ["CUDA_VISIBLE_DEVICES"] = "" # device: cpu

# helper function

# return the total count of lines of this lang script
def countNumLines(langs, output_dir, data_path):
    direct = output_dir+langs+'/'
    if not os.path.exists(direct): 
        os.makedirs(direct)
    path = direct+langs+'.count.txt'
    count = []
    counted = False
    lang_list = langs.split('+')
    if os.path.isfile(path):
        if os.path.getsize(path)!=0:
            counted = True
    
    if counted:
        count = [int(x) for x in open(path,'r').readline().split(' ')]
    else:
        files = [(data_path+'{}.txt'.format(lang)) for lang in lang_list]
        n_langs = len(lang_list)
        count = [len(open(files[i], 'r', encoding='utf-8').readlines()) 
                 for i in range(n_langs)]
       
        with open(path, 'w') as f:
            count_str = [str(x) for x in count]
            f.write(' '.join(count_str))
    count_dic = {}
    for i, lang in enumerate(lang_list):
        count_dic[lang] = count[i]
    return count_dic

def tsplit(s, sep):
    stack = [s]
    for char in sep:
        pieces = []
        for substr in stack:
            pieces.extend(substr.split(char))
        stack = pieces
    return stack

def cleanThai(aline):
    ### hard code function
    clean_line = []
    for word in aline.split():
        maxchar = max(word)
        if u'\u0020' <= maxchar <= u'\u0040' or u'\u005b' <= maxchar <= u'\u0060' or u'\u007b' <= maxchar <= u'\u007e' or u'\u0e00' <= maxchar <= u'\u0e7f':
                clean_line.append(word)
    return ' '.join(clean_line)

# limit the length of aline to be within max_num_chars
def limitSentenceLength(aline, max_num_chars):
    orig = aline
    if len(aline) > max_num_chars:
        choices = tsplit(aline, '.!?')
        while aline == '': aline = random.choice(choices)
        #if aline=='': print('.!? empty\n',orig)
        if len(aline) > max_num_chars:
            choices = aline.split(',')
            while aline == '': aline = random.choice(choices)
            if len(aline) > max_num_chars:
                words = aline.split(' ')
                aline=''
                for i in range(len(words)):
                    pre_aline = aline
                    aline += (words[i]+' ')
                    if len(aline) > max_num_chars:
                        aline = pre_aline
                        break
    return aline.strip()

def prettify(elem):
    """Return a pretty-printed XML string for the Element.
    """
    rough_string = ElementTree.tostring(elem, 'utf-8')
    reparsed = minidom.parseString(rough_string)
    return reparsed.toprettyxml(indent="  ")
    #return rough_string

class picture:
    '''
    Args: 
        langs: e.g. tha+eng
        num_sentences: e.g. 2+2
        text_soure: raw text source, e.g. /data/DATA/
        font_source: a list, e.g. ['fontdir1/a.ttf', 'fontdir2/b.ttf]
        width: width of the line
        height: height of the line
        max_char: maximum character for one piece
    '''

    def __init__(self, langs, num_sentences, 
                 text_source, font_source, image_name, 
                 width=1000, height=32, total_height= 600,
                 intervel=10, padding=10, min_num_lines=4,
                 max_char=30, font_size=20, 
                 output_dir='../dataset/', train='train', database='Unspecified'):
        self.langs = langs.split('+')
        self.num_sens = num_sentences
        self.source = text_source
        self.width = width
        self.height = height
        self.total_height = total_height
        self.max_char = max_char
        self.font_size = font_size
        self.train = train
        self.intervel = intervel
        self.padding = padding
        self.min_num_lines = min_num_lines
        self.image = self.create_image()
        self.fonts = self._get_font(font_source)
        self.counts = countNumLines(langs, output_dir, text_source)
        self.image_name = self._get_image_name(output_dir, image_name)
        self.database = database
        
        self._draw_on_image()
    
    def _get_image_name(self, output_dir, image_name):
        '''
        return the path of the image that needs to be generated
        '''
        
        path = output_dir+'+'.join(self.langs)+'/{}/image/'.format(self.train)
        if not os.path.exists(path):
            os.makedirs(path)
        return path+image_name
    
    def _get_font(self, font_source):
        '''
        return a dictionary whose values are ImageFont object
        '''
        
        fonts = {}
        self.ys = {}
        self.fonts_info = {}
        draw = ImageDraw.Draw(self.image)
        
        min_d = self.height
        max_lang = ''
        for i, lang in enumerate(self.langs):
            fontsize = self.font_size
            # take care of font size and image height
            fontobj = ImageFont.truetype(font_source[i], fontsize)
            h = draw.textsize(font=fontobj, text=' ')[1]
            while h > self.height:
                fontsize -= 1
                fontobj = ImageFont.truetype(font_source[i], fontsize)
                h = draw.textsize(font=fontobj, text=' ')[1]
            self.fonts_info[lang] = {}
            self.fonts_info[lang]['font'] = font_source[i]
            self.fonts_info[lang]['fontsize'] = fontsize
            fonts[lang] = ImageFont.truetype(font_source[i], fontsize)
            self.ys[lang] = (self.height-h)//2
            
            if self.ys[lang] < min_d: 
                min_d = self.ys[lang]
                min_lang = lang
        for lang in self.ys.keys():
            y = self.ys[lang]
            self.ys[lang] = y+(y-min_d)
        return fonts
    def create_image(self):
        '''
        Creates a basic PIL image previously fixing its size
        '''
        return Image.new("RGBA", (self.width, self.total_height))
    
    def _init_segmentation(self):
        self.segmentation = {}
        for lang in self.langs:
            self.segmentation[lang] = []
    
    
    def _pick_text(self, lang):
        text = linecache.getline(self.source+'{}.txt'.format(lang), 
                                 random.randint(0, self.counts[lang])
                                ).strip('\n')
        if lang == 'tha':
            text = cleanThai(text)
        return limitSentenceLength(text, self.max_char)
    
    def _draw_on_image(self):
        # blank segmentation
        #self._init_segmentation()
        # add text to picture
        draw = ImageDraw.Draw(self.image)
        
        inbetween = random.randint(self.intervel-2, self.intervel+2)
        max_num_lines = self.total_height//(self.height+inbetween)
        #print('max_num_lines', max_num_lines)
        num_lines = random.randint(self.min_num_lines, max_num_lines)
        
        self.segmentations = [[] for _ in range(num_lines)]
        self.lines = [{} for _ in range(num_lines)]
        
        left = random.randint(1, self.padding)
        #print('left', left, 'padding', self.padding)
        box = {}
        for i in range(num_lines):
            box = {}
            y0 = i*(self.height+inbetween)
            #print('y0', y0)
            cur_left = left
            prev_lang = ''
            cur_lang = ''
            prev_text = ''
            
            # pick text
            texts = []
            langs = self.langs
            if len(langs) > 3: 
                langs = random.sample(self.langs, 3)
            for lang in langs:
                for n in self.num_sens:
                    texts.append((lang, self._pick_text(lang)))
            # shuffle sequence
            shuffle(texts)
            
            
            # add xmin, xmax, ymin, ymax to line
            self.lines[i]['xmin'] = cur_left
            self.lines[i]['xmax'] = cur_left
            self.lines[i]['ymin'] = y0+min(self.ys.values())
            self.lines[i]['ymax'] = y0+max(self.ys.values())
            
            for lang, text in texts:
                prev_text = ''
                xmin = cur_left
                if lang == prev_lang: # merge the previous box with the cur box
                    #prev_box = self.segmentation[prev_lang].pop()
                    prev_box = self.segmentations[i].pop()
                    xmin = prev_box['xmin']
                    prev_text = prev_box['text']+' '
                box = {}
                fontobj = self.fonts[lang]
                w, h = draw.textsize(font=fontobj, text=text+' ')
                next_left = cur_left + w
                
                iterations = 0
                while next_left > self.width :
                    iterations += 1
                    #text = text[:len(text)//2] # half the textline
                    text = limitSentenceLength(text, len(text)//2)
                    next_left = cur_left + draw.textsize(font=fontobj, text=text+' ')[0]
                    if iterations >=10: 
                        break
                text = text.strip() # strip extra spaces
                if (iterations >= 5) or (len(prev_text+text) < 4): 
                    next_left = cur_left
                    if prev_text != '':
                        #self.segmentation[prev_lang].append(prev_box)
                        self.segmentations[i].append(prev_box)
                    continue
                
                if cur_left + draw.textsize(font=fontobj, text=text)[0] - xmin > 33:
                    draw.text((cur_left, self.ys[lang]+y0), text+' ', font=fontobj, fill=(0,0,0,255))
                    box['xmin'] = xmin
                    box['xmax'] = cur_left + draw.textsize(font=fontobj, text=text)[0]
                    box['ymin'] = self.ys[lang]+y0
                    box['ymax'] = self.ys[lang]+y0+h
                    box['text'] = prev_text+text
                    #self.segmentation[lang].append(box)
                    box['language'] = lang
                    box['font'] = os.path.basename(self.fonts_info[lang]['font'])
                    box['fontsize'] = self.fonts_info[lang]['fontsize']
                    self.segmentations[i].append(box)
                    # update line xmax, ymax
                    if box['xmax'] > self.lines[i]['xmax']:
                        self.lines[i]['xmax'] = box['xmax']
                    if box['ymax'] > self.lines[i]['ymax']:
                        self.lines[i]['ymax'] = box['ymax']
                    prev_lang = lang
                    prev_box = {}

                cur_left = next_left
        # save the image
        self.image.save(self.image_name, "png")
        # change to jpg format
        png = Image.open(self.image_name)
        png.load() # required for png.split()

        background = Image.new("RGB", png.size, (255, 255, 255))
        background.paste(png, mask=png.split()[3]) # 3 is the alpha channel
        background.save(os.path.splitext(self.image_name)[0]+'.jpg', 'JPEG', quality=100)
        os.remove(self.image_name)
        self.image_name = os.path.splitext(self.image_name)[0]+'.jpg'
    
    def create_xml(self, outname, folder='image', depth=3, is_print=1):
        """Create the xml file"""
        out_dir = os.path.dirname(outname)
        if not os.path.exists(out_dir):
            os.mkdir(out_dir)
        
        
        top = Element('annotation')
        child_folder = SubElement(top, 'folder')
        child_folder.text = os.path.dirname(self.image_name)

        filename = os.path.basename(self.image_name)
        child_filename = SubElement(top, 'filename')
        child_filename.text = filename

        child_source = SubElement(top, 'source')
        child_source_database = SubElement(child_source, 'database')
        child_source_database.text = self.database
        
        child_source = SubElement(top, 'printed')
        child_source_database = SubElement(child_source, 'printed')
        child_source_database.text = str(is_print)

        child_size = SubElement(top, 'size')
        child_size_width = SubElement(child_size, 'width')
        child_size_width.text = str(self.width)
        child_size_height = SubElement(child_size, 'height')
        child_size_height.text = str(self.total_height)
        child_size_depth = SubElement(child_size, 'depth')
        child_size_depth.text = str(depth)
        
        
        child_line = {}
        child_line_size = {}
        child_line_size_width = {}
        child_line_size_height = {}
        child_line_size_depth = {}
        
        child_line_bndbox = {}
        child_line_bndbox_xmin = {}
        child_line_bndbox_ymin = {}
        child_line_bndbox_xmax = {}
        child_line_bndbox_ymax = {}
        

        for j in range(len(self.segmentations)):
            child_line[j] = SubElement(top, 'line')
            child_line_size[j] = SubElement(child_line[j], 'size')
            child_line_size_width[j] = SubElement(child_line_size[j], 'width')
            child_line_size_width[j].text = str(self.width)
            child_line_size_height[j] = SubElement(child_line_size[j], 'height')
            child_line_size_height[j].text = str(self.height)
            child_line_size_depth[j] = SubElement(child_line_size[j], 'depth')
            child_line_size_depth[j].text = str(depth)
            
            child_object = {}
            child_object_language = {}
            child_object_bndbox = {}
            child_object_bndbox_text = {}
            child_object_bndbox_xmin = {}
            child_object_bndbox_ymin = {}
            child_object_bndbox_xmax = {}
            child_object_bndbox_ymax = {}
            for i, seg in enumerate(self.segmentations[j]):
                child_object[i] = SubElement(child_line[j], 'object')
                child_object_language[i] = SubElement(child_object[i], 'language')
                child_object_language[i].text = str(seg['language'])

                child_object_bndbox[i] = SubElement(child_object[i], 'bndbox')
                child_object_bndbox_xmin[i] = SubElement(child_object_bndbox[i], 'xmin')
                child_object_bndbox_xmin[i].text = str(seg['xmin'])
                child_object_bndbox_ymin[i] = SubElement(child_object_bndbox[i], 'ymin')
                child_object_bndbox_ymin[i].text = str(seg['ymin'])
                child_object_bndbox_xmax[i] = SubElement(child_object_bndbox[i], 'xmax')
                child_object_bndbox_xmax[i].text = str(seg['xmax'])
                child_object_bndbox_ymax[i] = SubElement(child_object_bndbox[i], 'ymax')
                child_object_bndbox_ymax[i].text = str(seg['ymax'])

                child_object_bndbox_text[i] = SubElement(child_object_bndbox[i], 'text')
                child_object_bndbox_text[i].text = str(seg['text'])
                child_object_bndbox_text[i] = SubElement(child_object_bndbox[i], 'font')
                child_object_bndbox_text[i].text = str(seg['font'])
                child_object_bndbox_text[i] = SubElement(child_object_bndbox[i], 'fontsize')
                child_object_bndbox_text[i].text = str(seg['fontsize'])

        #tree = ET.ElementTree(top)
        string = prettify(top)
        #print(string)
        with open(outname, 'w', encoding='utf-8') as f:
            f.write(string)
        return top

def main(num_ins, 
         langs, output_folder,
         num_sentences, 
         height, 
         total_height,
         font_size, 
         train, 
         text_source, 
         fonts_dir, 
         max_char ):
    # get all available fonts
    fonts_list =[]
    for i in fonts_dir:
        fonts_list.append(glob.glob(os.path.join(i,'*'))) 
    for i in range(num_ins):
        font_choice = [random.choice(x) for x in fonts_list]
        pic = picture(langs=langs,num_sentences=num_sentences, text_source=text_source,font_source=font_choice, 
                      image_name='{}.png'.format(i), font_size=font_size, output_dir=output_folder, 
                      height=height, total_height=total_height, train=train, max_char=max_char)
        pic.create_xml(os.path.join(output_folder,'{}/{}/xml/{}.xml'.format(langs, train, i)))
    

if __name__=='__main__':
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--langs", type=str, help="languages separated by +, e.g. tha+eng")
    p.add_argument("--num_sentences", type=str, help="number of sentences for each language separated by +, e.g. 2+2")
    p.add_argument("--text_source", type=str, help="folder of the source txt, e.g. /data/DATA/")
    p.add_argument("--font_dir", nargs = '*', help="font directoriess separated by ' ', e.g. thafontsdir engfontsdir")
    p.add_argument("--output_folder", type=str, default='../dataset/', help="output dataset folder path, defualt: '../dataset/'")
    p.add_argument("--num_instances", type=int, default=1, help="number of examples to generate")
    p.add_argument("--line_height", type=int, default=32, help="the height of one text line, default=32")
    p.add_argument("--pic_height", type=int, default=600, help="the height of the picture, default=600")
    p.add_argument("--font_size", type=int, default=20, help="the upper bound of font size, will be adjusted if the font height is higher than the height of line")
    p.add_argument("--train", type=bool, default=True, help="a boolean value tells if it is training data, default: True")
    p.add_argument("--max_char", type=int, default=40, help="the max number of characters for one piece of language text")
    args = p.parse_args()
    train = 'train'
    if not args.train:
        train = 'eval'
    num_sentences = [int(x) for x in args.num_sentences.split('+')]
    fonts_dir = args.font_dir#[x for x in args.font_dir.split()]
    main(args.num_instances,
         args.langs, args.output_folder,
         num_sentences,
         args.line_height,
         args.pic_height,
         args.font_size,
         train,
         args.text_source,
         fonts_dir,
         args.max_char)
