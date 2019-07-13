import os
import cv2
from lxml import etree
import xml.etree.cElementTree as ET
import sys


obj = sys.argv[1]
image_folder = sys.argv[2]
savedir = sys.argv[3]
imgsavedir = sys.argv[4]
if __name__ == '__main__':
    for n, image_file in enumerate(os.scandir(image_folder)):
        if (image_file != '.DS_Store') :
            image = cv2.imread(image_file.path)
            newpath = imgsavedir + '/' + image_file.name
            try:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2RGB)
            except:
                os.rename(image_file.path, newpath)
                continue
            img = image_file

            if not os.path.isdir(savedir):
                os.mkdir(savedir)

            image = cv2.imread(img.path)
            height, width, depth = image.shape

            annotation = ET.Element('annotation')
            ET.SubElement(annotation, 'folder').text = image_folder
            ET.SubElement(annotation, 'filename').text = image_file.name
            ET.SubElement(annotation, 'segmented').text = '0'
            size = ET.SubElement(annotation, 'size')
            ET.SubElement(size, 'width').text = str(width)
            ET.SubElement(size, 'height').text = str(height)
            ET.SubElement(size, 'depth').text = str(depth)

            ob = ET.SubElement(annotation, 'object')
            ET.SubElement(ob, 'name').text = obj
            ET.SubElement(ob, 'pose').text = 'Unspecified'
            ET.SubElement(ob, 'truncated').text = '0'
            ET.SubElement(ob, 'difficult').text = '0'
            bbox = ET.SubElement(ob, 'bndbox')
            ET.SubElement(bbox, 'xmin').text = str(0)
            ET.SubElement(bbox, 'ymin').text = str(0)
            ET.SubElement(bbox, 'xmax').text = str(width)
            ET.SubElement(bbox, 'ymax').text = str(height)

            xml_str = ET.tostring(annotation)
            root = etree.fromstring(xml_str)
            xml_str = etree.tostring(root, pretty_print=True)
            print(image_file.name)
            replacementstring = image_file.name.split(".")[0]
            replacementstring=replacementstring +'.xml'
            print("aaaa")
            print(replacementstring)
            save_path = os.path.join(savedir, replacementstring)
            print(save_path)
            with open(save_path, 'wb') as temp_xml:
                temp_xml.write(xml_str)
            print(image_file.path)
            print(newpath)
            os.rename(image_file.path, newpath)

