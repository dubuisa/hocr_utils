
# hocr_utils

![ci_master](https://github.com/Mrmarx/hocr_utils/workflows/CI/badge.svg?branch=master)

![pypi_package_version](https://img.shields.io/pypi/v/hocr-utils.svg?color=blue)

![pypi_python_version](https://img.shields.io/pypi/pyversions/hocr-utils.svg)

**hocr_utils** is a package to transform, plot and simplify the use of hOCR files.

# Installation

## Dependencies

hocr-utils requires:

- Python (>= |3.7|)

## Optional Dependencies

The functions to plot, transform pdf into hOCR require the following additional dependencies:

- pytesseract
- pdf2image
- opencv-python

Additionaly tesseract language pack need to be install for non-english ocr.

Example: install french language package on ubuntu with:

```bash
apt-get install tesseract-ocr-fra
```

## User Installation

The easiest way to install scikit-learn is using `pip`:

```bash
pip install -U hocr_utils

```
    
# Usecases

## Transform PIL Images to hOCR

Requires `pytesseract` dependency and the requested tesseract language pack.

```python
from hocr_utils import utils
from PIL import Image

image = Image.open('./data/sample.png')
hocr = utils.images_to_hocr([image])
```

## Transform pdf to hOCR

Requires `pytesseract`, `pdf2image` dependencies as well as the requested tesseract language pack.


```python
from hocr_utils import utils

hocr = utils.pdf_to_hocr('./data/sample.pdf')
```

## Transform hOCR to list of dictionary

```python
from hocr_utils import utils

hocr_dict = utils.hocr_to_dict(hocr)
```
This can then be transformed into pandas dataFrame using `pd.dataFrame.from_records(hocr_dict)`

By default there will be one entry per line in the hOCR, However it is possible to group the list by `['paragraph', 'line', 'word']` using `by` argument.

## Get a single page from hOCR

```python
from hocr_utils import utils

hocr_1 = utils.get_page(hocr, 1)
```