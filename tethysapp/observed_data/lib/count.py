import os
from xml.dom import minidom

path = os.path.join(os.path.dirname(__file__),"test")

count =0


for filename in os.listdir(path):
	filePath = path + '/' +filename
	f=open(filePath,'r')
	content = f.read()
	xml = minidom.parseString(content)
	count += len(xml.getElementsByTagName('Site'))
 

print count