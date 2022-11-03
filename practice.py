from PIL import Image, ImageDraw
import pandas as pd

mapImage = Image.open('BLEAppMap.png')
dataFile = pd.read_csv('RSSITable.csv')

drawImage = ImageDraw.Draw(mapImage)  

for i in range(len(dataFile)):
    leftUpPoint = (dataFile.loc[i, 'x'] - 10, dataFile.loc[i, 'y'] - 10)
    rightDownPoint = (dataFile.loc[i, 'x'] + 10, dataFile.loc[i, 'y'] + 10)
    twoPointList = [leftUpPoint, rightDownPoint]
    drawImage.ellipse(twoPointList, fill=(255,0,0,255))

mapImage.show()