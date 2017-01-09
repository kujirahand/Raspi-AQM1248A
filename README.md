# Raspi-AQM1248A

AQM1248A Python library for Raspberry Pi

## USAGE:

Simple usage : fill display

```python:test1.py
from PIL import Image
import AQM1248A

disp = AQM1248A.LCD()
disp.show(Image.open('test.png'))
disp.close()
```

Drawing Bitmap

```python:test2.py
import AQM1248A
from PIL import Image

disp = AQM1248A.LCD()
image = Image.open('test.png')
disp.show(image)
disp.close()
```


