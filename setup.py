"""Information and settings for setuptools.setup(). Now the package can be installed with 'pip install .'."""
from setuptools import setup, find_packages
import versioneer

setup(name='asui',
      version=versioneer.get_version(),
      description='User interface to ai_svmbir.',
      url='',
      author='Jean Bilheux, Venkatrishnan (Venkat) Singanallur, Shimin Tang',
      author_email='bilheuxjm@ornl.gov, venkatakrisv@ornl.gov, tangs@ornl.gov ',
      license='',
      packages=find_packages(where='src'),
      package_dir={'': 'src'},
      scripts=["scripts/asui"],
      # Requirements are handled by conda
      #install_requires=['qtpy', 'pyqtgraph=0.11.0', 'pillow', 'tomopy', 'PyQt5', 'scikit-image', "NeuNorm"],
      extras_require=dict(tests=['pytest']),
      zip_safe=False)
