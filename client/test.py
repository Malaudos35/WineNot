
import requests
# from PIL import Image
# from io import BytesIO

url = "https://images.vivino.com/thumbs/LBpW05HDQzmDEm9m4YvrWw_375x500.jpg"
response = requests.get(url)

import imageio.v3 as iio

img = iio.imread(response.content)
h, w = img.shape[:2]
print(f"{w}x{h}")
