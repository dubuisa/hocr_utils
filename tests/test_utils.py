import os
import sys
import logging

import numpy as np

import pytest

from bs4 import BeautifulSoup
from PIL import Image

from hocr_utils import utils



SAMPLE_HOCR = """
<html>
    <body>
        <div id="page_1" class="ocr_page">
        <div class="ocr_carea" id="A" title="bbox 100 200 300 400">
            <span class="ocr_line" id="B" title="bbox 10 20 30 40">
                <span class="ocrx_word" id="C" title="bbox 1 2 3 4"> 1</span>
                <span class="ocrx_word" id="D" title="bbox 5 6 7 8">2 </span>
            </span>
            <span class="ocr_line" id="E" title="bbox 50 60 70 80">
                <span class="ocrx_word" id="F" title="bbox 9 10 11 12"> 3 </span>
                <span class="ocrx_word" id="G" title="bbox 13 14 15 16">4</span>
            </span>
        </div>
        </div>
    </body>
</html>
"""


@pytest.fixture()
def module_import_error(monkeypatch):
    monkeypatch.setitem(sys.modules, "pytesseract", None)
    monkeypatch.setitem(sys.modules, "cv2", None)


def test_pdf_to_hocr_import_error(module_import_error, caplog):
    caplog.set_level(logging.ERROR)
    value = utils.pdf_to_hocr("./to2moon.pdf")
    assert value is None
    assert "pip install" in caplog.text


def test_images_to_hocr_import_error(module_import_error, caplog):
    caplog.set_level(logging.ERROR)
    value = utils.images_to_hocr([np.zeros((3, 1, 1))])
    assert value is None
    assert "pip install" in caplog.text


def test_draw_pdf_with_boxes_import_error(module_import_error, caplog):
    caplog.set_level(logging.ERROR)
    value = utils.draw_pdf_with_boxes(pdf_path="./FreedomIsSlavery.pdf")
    assert value is None
    assert "pip install" in caplog.text


def test_pdf_to_hocr_import_error(module_import_error, caplog):
    caplog.set_level(logging.ERROR)
    value = utils.pdf_to_hocr("./to2moon.pdf")
    assert value is None
    assert "pip install" in caplog.text


def test_images_to_hocr(mocker):
    mocker.patch("pytesseract.image_to_pdf_or_hocr", return_value=SAMPLE_HOCR)
    image = [np.zeros((3, 1, 1)), np.zeros((3, 1, 1))]
    hocr = utils.images_to_hocr(image)
    soup = BeautifulSoup(hocr, "lxml")
    hocr_pages = soup.find_all("div", {"class": "ocr_page"})
    assert hocr_pages[0]["id"] == "page_1"
    assert hocr_pages[1]["id"] == "page_2"


@pytest.fixture(autouse=True)
def test_pdf_to_hocr(tmpdir, mocker):

    FILENAME = "the_spice_must_flow.pdf"
    os.chdir(tmpdir)
    open(FILENAME, "a").close()
    mocker.patch("pytesseract.image_to_pdf_or_hocr", return_value=SAMPLE_HOCR)
    mocker.patch("pdf2image.convert_from_bytes", return_value=[np.zeros((3, 1, 1))])
    hocr = utils.pdf_to_hocr(FILENAME)
    soup = BeautifulSoup(hocr, "lxml")
    hocr_page = soup.find_all("div", {"class": "ocr_page"})[0]
    assert hocr_page["id"] == "page_1"


def test_get_page_request_existing_page():
    body = " ".join([f'<div class="ocr_page" id="page_{i+1}"></div>' for i in range(2)])
    hocr = f"<html><body>{body}</body></html>"
    assert utils.get_page(hocr, 1) == '<div class="ocr_page" id="page_2"></div>'


def test_get_page_request_non_existing_page():
    body = " ".join([f'<div class="ocr_page" id="page_{i+1}"></div>' for i in range(2)])
    hocr = f"<html><body>{body}</body></html>"
    page_index = 42

    try:
        utils.get_page(hocr, page_index)
        pytest.fail()
    except ValueError as e:
        assert str(page_index) in str(e)


@pytest.mark.parametrize("expected_length", [(1), (2), (3)])
def test_len_pages(expected_length):
    body = " ".join(
        [
            f'<div class="ocr_page" id="page_{i+1}"></div>'
            for i in range(expected_length)
        ]
    )
    hocr = f"<html><body>{body}</body></html>"
    assert expected_length == utils.len_pages(hocr)


def test_len_pages_empty_hocr():
    hocr = f"<html><body></body></html>"
    assert 0 == utils.len_pages(hocr)


def test_get_text():
    span_words = " ".join([f"<span>{w}</span>" for w in ["hello", "world"]])
    span_line = f'<span class="ocr_line">{span_words}</span>'
    body = " ".join(
        [f'<div class="ocr_page" id="page_{i+1}">{span_line}</div>' for i in range(2)]
    )
    hocr = f"<html><body>{body}</body></html>"

    assert utils.get_text(hocr) == "hello world\nhello world"


def test_get_text_with_page_number():
    span_words = " ".join([f"<span>{w}</span>" for w in ["hello", "world"]])
    span_line = f'<span class="ocr_line">{span_words}</span>'
    body = " ".join(
        [f'<div class="ocr_page" id="page_{i+1}">{span_line}</div>' for i in range(2)]
    )
    hocr = f"<html><body>{body}</body></html>"

    assert utils.get_text(hocr, 1) == "hello world"


def test_get_lang():
    body = " ".join(
        [
            f'<span class="ocr_line" lang="{lang}"></span>'
            for lang in ["fra", "eng", "eng"]
        ]
    )
    hocr = f"<html><body>{body}</body></html>"
    assert utils.get_lang(hocr) == "eng"


def test_get_lang_no_lang_defined():
    hocr = f"<html><body></body></html>"
    assert utils.get_lang(hocr, "unk") == "unk"


@pytest.mark.parametrize(
    "by,text,n_element,id_,x1,y1,x2,y2",
    [
        ("paragraph", "1 2\n3\n4", 1, "A", 100, 200, 300, 400),
        ("line", "1 2", 2, "B", 10, 20, 30, 40),
        ("word", "1", 4, "C", 1, 2, 3, 4),
    ],
)
def test_hocr_as_dict(by, text, n_element, id_, x1, y1, x2, y2):

    r = utils.hocr_as_dict(SAMPLE_HOCR, by=by)
    assert len(r) == n_element
    assert r[0]["text"] == text
    assert r[0]["page"] == 0
    assert r[0]["x1"] == x1
    assert r[0]["y1"] == y1
    assert r[0]["x2"] == x2
    assert r[0]["y2"] == y2
    assert r[0]["id"] == id_
    assert r[0]["len_text"] == len(text)


def test_extract_bbox():
    x1, y1, x2, y2 = utils._extract_bbox("bbox 1 2 3 4;")
    assert x1 == 1
    assert y1 == 2
    assert x2 == 3
    assert y2 == 4


@pytest.mark.parametrize(
    "pdf_path,pdf_bytes,hocrs,hocr_dict,page_id",
    [
        ("./1.pdf", None, None, None, None),
        (None, bytes(1), None, None, None),
        ("./1.pdf", None, "hocr", None, None),
        ("./1.pdf", None, None, [{"page": 0}, {"page": 1}], None),
        ("./1.pdf", None, None, [{"page": 0}, {"page": 1}], 1),
    ],
)
def test_draw_pdf_with_boxes(pdf_path, pdf_bytes, hocrs, hocr_dict, page_id, mocker):
    # pdf_path=None, hocrs=None, page_id=None, hocr_dict = None,
    images = [np.zeros((3, 1, 1)), np.zeros((3, 1, 1))]
    m1 = mocker.patch("pdf2image.convert_from_bytes", return_value=images)
    m2 = mocker.patch("pdf2image.convert_from_path", return_value=images)
    m3 = mocker.patch(
        "hocr_utils.utils.hocr_as_dict",
        return_value=[{"page": 0}, {"page": 0}, {"page": 1}],
    )
    m4 = mocker.patch("hocr_utils.utils._image_with_boxes", return_value=images)

    returned_values = utils.draw_pdf_with_boxes(
        pdf_path=pdf_path,
        pdf_bytes=pdf_bytes,
        hocrs=hocrs,
        hocr_dict=hocr_dict,
        page_id=page_id,
    )
    expected_page_len = 2 if page_id is None else 1
    assert len(returned_values) == expected_page_len

    m1.assert_called() if pdf_path is None else m2.assert_called()
    if hocrs is not None:
        m3.assert_called()


def test_image_with_boxes(mocker):
    m = mocker.patch("cv2.rectangle", return_value=None)

    lines = [
        {'x1': 1, 'y1': 2, 'x2': 3, 'y2': 4},
        {'x1': 1, 'y1': 2, 'x2': 3, 'y2': 4}
    ]

    img = Image.fromarray(np.zeros((3,10,10)).astype('uint8'), 'RGB')
    utils._image_with_boxes(img, lines)
    m.assert_called()