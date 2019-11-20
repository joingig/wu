from PIL import Image
from sys import exit


def isLookstheSame (a, b, dev=10):
    #print "a is {}".format(a)
    #print "b is {}".format(b)
    
#    print "a-b is {}".format(a-b)
    if abs(a[0]-b[0]) < dev and abs(a[1]-b[1]) < dev and abs(a[2]-b[2]) < dev:
        return True
    return False

img_a = 'wsymbol_0008_clear_sky_night.png'
img_n = 'wu'+img_a

#pic = Image.open(img_a).resize((50,50))
pic = Image.open(img_a)
pic_a = pic.convert("RGBA")

data = pic_a.getdata()

pix = data[5]
print "[**] pix data: {}".format(pix)
#(197, 197, 197, 255)
#(147, 147, 147, 255)
#(64, 72, 145, 255)
#print pic_a.mode
newData = []
for item in data:
    #print item
    if isLookstheSame(pix, item, 13):
        print "Looks the same {} and {}".format(pix,item)
        newData.append((255, 255, 255, 0))
    else:
        print "Looks like {} and {} diff".format(pix,item)
        newData.append(item)
    #if item[0] == 197 and item[1] == 197 and item[2] == 197:
    #if item[0] == pix[0] and item[1] == pix[1] and item[2] == pix[2]:
    #if item == pix:
    #    newData.append((255, 255, 255, 0))
    #else:
    #    newData.append(item)

pic_a.putdata(newData)
pic_a.save(img_n, "PNG")
print "new file {} writed".format(img_n)
