from setuptools import find_packages
from setuptools import setup
import pathlib

HERE = pathlib.Path(__file__).parent
INSTALL_REQUIRES = (HERE / "requirements.txt").read_text().splitlines()
TESTS_REQUIRE = (HERE / "test-requirements.txt").read_text().splitlines()[1:]
setup(name='hocr_utils',
      version="1.0",
      description="Package containing utility function for hOCR and tesseract",
      packages=find_packages(),
      install_requires=INSTALL_REQUIRES,
      tests_require=TESTS_REQUIRE,
      test_suite='tests',
      # include_package_data: to install data from MANIFEST.in
      include_package_data=True,
      zip_safe=False)
