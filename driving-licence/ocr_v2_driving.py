# import the necessary packages
from PIL import Image
import pytesseract
import argparse
import cv2
import os
import re
import io
import json
import ftfy
# from nostril import nonsense


################################################################################################################
############################# Section 1: Initiate the command line interface ###################################
################################################################################################################

# construct the argument parse and parse the arguments
ap = argparse.ArgumentParser()
ap.add_argument("-i", "--image", required=True,
                help="path to input image to be OCR'd")
ap.add_argument("-p", "--preprocess", type=str, default="thresh",
                help="type of preprocessing to be done, choose from blur, linear, cubic or bilateral")
args = vars(ap.parse_args())

'''
Our command line arguments are parsed. We have two command line arguments:

--image : The path to the image we’re sending through the OCR system.
--preprocess : The preprocessing method. This switch is optional and for this tutorial and can accept the following 
                parameters to be passed (refer sections to know more:
                - blur
                - adaptive
                - linear
                - cubic
                - gauss
                - bilateral
                - thresh (meadian threshold - default)
                
---------------------------  Use Blur when the image has noise/grain/incident light etc. --------------------------
'''

##############################################################################################################
###################### Section 2: Load the image -- Preprocess it -- Write it to disk ########################
##############################################################################################################

# load the example image and convert it to grayscale
image = cv2.imread(args["image"])
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# check to see if we should apply thresholding to preprocess the
# image
if args["preprocess"] == "thresh":
    gray = cv2.threshold(gray, 0, 255,
                         cv2.THRESH_BINARY | cv2.THRESH_OTSU)[1]

elif args["preprocess"] == "adaptive":
    gray = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, cv2.THRESH_BINARY, 31, 2)
'''
What we would like to do is to add some additional preprocessing steps as in most cases, you may need to scale your 
image to a larger size to recognize small characters. 
In this case, INTER_CUBIC generally performs better than other alternatives, though it’s also slower than others.

If you’d like to trade off some of your image quality for faster performance, 
you may want to try INTER_LINEAR for enlarging images.
'''
if args["preprocess"] == "linear":
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_LINEAR)

elif args["preprocess"] == "cubic":
    gray = cv2.resize(gray, None, fx=2, fy=2, interpolation=cv2.INTER_CUBIC)

# make a check to see if blurring should be done to remove noise, first is default median blurring

if args["preprocess"] == "blur":
    gray = cv2.medianBlur(gray, 3)

elif args["preprocess"] == "bilateral":
    gray = cv2.bilateralFilter(gray, 9, 75, 75)

elif args["preprocess"] == "gauss":
    gray = cv2.GaussianBlur(gray, (5,5), 0)

# write the grayscale image to disk as a temporary file so we can
# apply OCR to it
filename = "{}.png".format(os.getpid())
cv2.imwrite(filename, gray)

##############################################################################################################
######################################## Section 3: Running PyTesseract ######################################
##############################################################################################################


# load the image as a PIL/Pillow image, apply OCR, and then delete
# the temporary file
text = pytesseract.image_to_string(Image.open(filename), lang = 'eng')
# add +hin after eng within the same argument to extract hindi specific text - change encoding to utf-8 while writing
os.remove(filename)
# print(text)

# show the output images
# cv2.imshow("Image", image)
# cv2.imshow("Output", gray)
# cv2.waitKey(0)

# writing extracted data into a text file
text_output = open('outputbase.txt', 'w', encoding='utf-8')
text_output.write(text)
text_output.close()

file = open('outputbase.txt', 'r', encoding='utf-8')
text = file.read()
# print(text)

# Cleaning all the gibberish text
text = ftfy.fix_text(text)
text = ftfy.fix_encoding(text)
'''for god_damn in text:
    if nonsense(god_damn):
        text.remove(god_damn)
    else:
        print(text)'''
# print(text)

############################################################################################################
###################################### Section 4: Extract relevant information #############################
############################################################################################################

# Initializing data variable
surname = None
dob = None
doe = None
number = None
text0 = []
text1 = []

# Searching for PAN
lines = text.split('\n')
for lin in lines:
    s = lin.strip()
    s = lin.replace('\n','')
    s = s.rstrip()
    s = s.lstrip()
    text1.append(s)

text1 = list(filter(None, text1))
# print(text1)

# to remove any text read from the image file which lies before the line 'Income Tax Department'

lineno = 0  # to start from the first line of the text file.

# text1 = list(text1)
text0 = text1[lineno+1:]
print(text0)  # Contains all the relevant extracted text in form of a list - uncomment to check

def findword(textlist, wordstring):
    lineno = -1
    for wordline in textlist:
        xx = wordline.split( )
        if ([w for w in xx if re.search(wordstring, w)]):
            lineno = textlist.index(wordline)
            textlist = textlist[lineno+1:]
            return textlist
    return textlist

###############################################################################################################
######################################### Section 5: Dishwasher part ##########################################
###############################################################################################################
try:

    # Cleaning name
    name = text0[5]
    name = re.sub('[^a-zA-Z]+', ' ', name)
    name = name.rstrip()
    name = name.lstrip()

    # Cleaning DOB
    dob = text0[4]
    dob = dob.rstrip()
    dob = dob.lstrip()
    dob = dob[4:7]

    # Cleaning Passport Number
    number = text0[1]
    number = number[-21:-6]
    number = number.rstrip()
    number = number.lstrip()

    # Cleaning DOE
    doe = text0[14]
    doe = doe.rstrip()
    doe = doe.lstrip()
    doe = doe[-12:-2]

except:
    pass

# Making tuples of data
data = {}
data['Name'] = name
data['Date of Birth'] = dob
data['Number'] = number
data['Date of Expiry'] = doe

# print(data)

###############################################################################################################
######################################### Section 6: Write Data to JSONs ######################################
###############################################################################################################

# Writing data into JSON
try:
    to_unicode = unicode
except NameError:
    to_unicode = str

# Write JSON file
with io.open('data.json', 'w', encoding='utf-8') as outfile:
    str_ = json.dumps(data, indent=4, sort_keys=True, separators=(',', ': '), ensure_ascii=False)
    outfile.write(to_unicode(str_))

# Read JSON file
with open('data.json', encoding = 'utf-8') as data_file:
    data_loaded = json.load(data_file)

# print(data == data_loaded)

# Reading data back JSON(give correct path where JSON is stored)
with open('data.json', 'r', encoding= 'utf-8') as f:
    ndata = json.load(f)

print(ndata)