import re
import tempfile
import logging

from bs4 import BeautifulSoup
import numpy as np


BS4_PARSER = "lxml"
BBOX_MAPPING = {"paragraph": "ocr_carea", "line": "ocr_line", "word": "ocrx_word"}

logger = logging.getLogger(__name__)


def images_to_hocr(images, lang="fra+deu+ita+eng", config="--psm 4"):
    """Transforms a list of PIL images into an hOCR file.

    Parameters
    ----------
    images : List
        List of PIL images
    lang: str, optional (default="fra+deu+ita+eng")
        Supporter Language of Pytesseract. 
    config: str, optional (default = "--psm 4")
        Custom configuration flag used by Tesseract
    """

    try:
        import pytesseract
    except ImportError:
        logger.error(
            "pytesseract have to be installed to use this function\n run `pip install -U pytesseract`"
        )
        return

    hocrs = [
        pytesseract.image_to_pdf_or_hocr(
            image, lang=lang, config=config, extension="hocr"
        )
        for image in images
    ]

    return _merge_hocr(hocrs)


def pdf_to_hocr(path, lang="fra+deu+ita+eng", config="--psm 4"):
    """Loads and transform a pdf into an hOCR file.

    Parameters
    ----------
    path : str, required
        The pdf's path
    lang: str, optional (default="fra+deu+ita+eng")
        Supporter Language of Pytesseract. 
    config: str, optional (default = "--psm 4")
        Custom configuration flag used by Tesseract
    """

    try:
        import pytesseract
        from pdf2image import convert_from_bytes
    except ImportError:
        logger.error(
            "pytesseract and pdf2image have to be installed to use this function\n run `pip install -U pytesseract pdf2image`"
        )
        return

    with open(path, "rb") as f:
        images = convert_from_bytes(f.read(), dpi=300)
        return images_to_hocr(images)


def get_page(hocr, page_index):
    """
    Gets the page according to the page_index parameter

    Parameters
    ----------
    hocr : str, required
        an hOCR Document
    page_index: str, required
        The index of the page to be returned
    """

    soup = BeautifulSoup(hocr, BS4_PARSER)
    result = soup.find("div", {"id": f"page_{page_index+1}"})
    if result:
        return str(result)
    raise ValueError(
        f"The requested page {page_index} does not exists on the provided hocr."
    )


def len_pages(hocr):
    """
    Returns the number of pages

    Parameters
    ----------
    hocr : str, required
        an hOCR Document
    """
    soup = BeautifulSoup(hocr, BS4_PARSER)
    return len(soup.find_all("div", {"class": "ocr_page"}))


def get_text(hocr, page_index=None):
    """
    Returns the textual content of the text or the content of the specified `page_index`

    Parameters
    ----------
    hocr : str, required
        an hOCR Document
    page_index: str, required
        The index of the page to be returned
    """

    if page_index:
        hocr = get_page(hocr, page_index)

    soup = BeautifulSoup(hocr, BS4_PARSER)
    lines = soup.find_all("span", ["ocr_line", "ocr_caption"])
    return "\n".join([line.text.replace("\n", " ").strip() for line in lines])


def get_lang(hocr, default_lang="fra"):
    """
    Retrieves the most represented language, returns `default_lang` if language is undefined in hocr
    
    Parameters
    ----------
    hocr : str, required
        an hOCR Document
    default_lang: str, optional (default='fra')
        The default language if the language is undefined
    """

    langs = re.findall(r'lang="([a-z]{3})"', hocr)
    if len(langs) == 0:
        return default_lang
    return max(set(langs), key=langs.count)


def hocr_to_dict(hocr, by="line"):
    """
    Return hocr as list of dict splited on "by" parameter

    Parameters
    ----------
    hocr : str
        hocr file
    by : str, optional (default = 'line')
        type of bbox, choose on ['paragraph', 'line', 'word']
    """

    hocr_list = []
    bbox_class = BBOX_MAPPING.get(by, "ocr_line")

    for i in range(len_pages(hocr)):
        page = get_page(hocr, i)
        lines = BeautifulSoup(page, BS4_PARSER).find_all(
            ["div", "span"], {"class": bbox_class}
        )

        for line in lines:
            x1, y1, x2, y2 = _extract_bbox(line["title"])
            text = re.sub(r"\n", " ", line.text)
            text = re.sub(r"\s{2,}", "\n", text).strip()
            if text:
                hocr_dict = {
                    "id": line["id"],
                    "page": i,
                    "x1": x1,
                    "y1": y1,
                    "x2": x2,
                    "y2": y2,
                    "text": text,
                    "len_text": len(text),
                }
                hocr_list.append(hocr_dict)
    return hocr_list


def draw_pdf_with_boxes(
    pdf_path=None,
    pdf_bytes=None,
    hocrs=None,
    by="line",
    page_id=None,
    hocr_dict=None
):
    """
    Plot each pdf page with its corresponding recognize boxes of texts.

    Parameters
    ----------
    pdf_path : str
        the path of the pdf file
    hocrs : str
        the corresponding hocr file
    by : str, optional (default = 'line')
        type of bbox, choose on ['paragraph', 'line', 'word']
    page_id: int, optional (default = None)
        argument to specify a single page of the pdf
    pdf_bytes
    """

    try:
        from pdf2image import convert_from_path, convert_from_bytes
        import cv2
    except ImportError:
        logger.error(
            "pdf2image and cv2 have to be installed to use this function\n run `pip install -U pdf2image opencv-python`"
        )
        return

    if pdf_bytes is not None:
        images = convert_from_bytes(pdf_bytes)
    else:
        images = convert_from_path(pdf_path, 300)

    if hocr_dict is None:
        hocr_dict = hocr_to_dict(hocrs, by)
    images_output = []
    for i, img in enumerate(images):
        if page_id is None or i == page_id:
            lines = [l for l in hocr_dict if l["page"] == i]
            images_output.append(_image_with_boxes(img, lines))
    return images_output


def _extract_bbox(text):
    """
    Extracts the bounding box values from the text

    Parameters
    ----------
    text : str, required
    """

    return list(map(int, re.findall(r"bbox ((?:\d{1,}\s?){4})", text)[0].split(" ")))


def _image_with_boxes(img, lines):
    import cv2

    img = np.array(img.convert("RGB"))
    for line in lines:
        cv2.rectangle(
            img, (line["x1"], line["y1"]), (line["x2"], line["y2"]), (255, 0, 0), 2
        )
    return img


def _merge_hocr(hocrs):
    """merge multiple hocrs file into 1 single hocr file following the defined standard"""

    base = hocrs[0]
    final_doc = BeautifulSoup(base, BS4_PARSER)
    for i, hocr in enumerate(hocrs[1:]):
        soup = BeautifulSoup(hocr, BS4_PARSER)
        hocr_page = soup.find_all("div", {"class": "ocr_page"})[0]
        hocr_page["id"] = f"page_{i + 2}"
        final_doc.body.append(hocr_page)
    return str(final_doc)
