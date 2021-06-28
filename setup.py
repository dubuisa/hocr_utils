from setuptools import find_packages
from setuptools import setup
import pathlib

with open("README.md", "r") as fh:
    long_description = fh.read()

HERE = pathlib.Path(__file__).parent
INSTALL_REQUIRES = (HERE / "requirements.txt").read_text().splitlines()
TESTS_REQUIRE = (HERE / "test-requirements.txt").read_text().splitlines()[1:]
setup(name='hocr_utils',
      version="0.0.1",
      author="Antoine Dubuis",
      author_email="antoine.dubuis@gmail.com",
      description="Package containing utility function for hOCR and tesseract",
      long_description_content_type="text/markdown",
      long_description=long_description,
      packages=find_packages(),
      url="https://github.com/Mrmarx/hocr_utils",
      install_requires=INSTALL_REQUIRES,
      tests_require=TESTS_REQUIRE,
      python_requires='>=3.7',
      keywords='hocr tesseract utility',
      test_suite='tests',
      project_urls={
        'Homepage': 'https://github.com/Mrmarx/hocr-utils',
      },
      classifiers=[
        'Programming Language :: Python :: 3.7',
        'Programming Language :: Python :: 3.8',
        'Programming Language :: Python :: 3.9',
        "Topic :: Utilities",
        "License :: OSI Approved :: MIT License",

      ],
      zip_safe=False)
