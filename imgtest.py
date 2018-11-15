from PIL import Image
from sys import exit
from os import path, getcwd

cdir=getcwd()

png_name="wsymbol_0001_sunny.png"
gif_test_name="clear.gif"

png_path=path.join(cdir, "wsymbol_0001_sunny.png")
gif_test_path=path.join(cdir, "clear.gif")


png = Image.open(png_name).convert("RGBA")
gif = Image.new("RGBA", png.size, (255,0,0,0))
gif_test = Image.open(gif_test_name)


#wsymbol_0001_sunny.png (150, 180, 228, 255)
#clear.gif 30
#img = gif_test.load()
#color = img[5,5]
#print color

png_data=png.getdata()
gif_data=[]

for item in png_data:
	if item==(150, 180, 228):
		gif_data.append((0,0,0))
	else:
		gif_data.append(item)


#gif.paste(png,png)
gif.putdata(gif_data)

print "GIF img {}".format(gif.info)
print "PNG img {}".format(png.info)
print "GIF_TEST img {}".format(gif_test.info)  

gif.save(path.splitext(png_name)[0]+".gif",'GIF',transparency=0)







