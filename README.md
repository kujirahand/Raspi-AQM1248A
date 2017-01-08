# Raspi-AQM1248A

AQM1248A Python library for Raspberry Pi

## USAGE:

Simple

```python:test1.py
import AQM1248A

disp = AQM1248A()
disp.full_display()
disp.close()
```

Drawing Bitmap

```python:test2.py
import AQM1248A
from PIL import Image

disp = AQM1248A()
image = Image.open('test.png')
disp.show(image)
disp.close()
```


