[![](https://img.shields.io/badge/python-3.7+-blue.svg)](https://www.python.org/downloads/)

Welcome to VolFe! an open-source framework for calculating melt-vapour equilibria including silicate melt, carbon, hydrogen, sulfur and noble gases. 

Read more about the python package in the Earth ArXiv pre-print (and please cite if you use the package!):
Hughes, E.C., Liggins, P., Wieser, P. and Stolper, E.M., 2024. VolFe: an open-source tool for calculating melt-vapor equilibria including silicate melt, carbon, hydrogen, sulfur, and noble gases. https://doi.org/10.31223/X52X3G 

For more information and worked examples, see the ReadTheDocs page:
https://volfe.readthedocs.io/en/latest/

VolFe can be installed using pip from PyPI or from GitHub (see notes below about installing an editable version).

## Development

If you wish to edit VolFe on your own computer, you can install an editable version using

```
pip install -e ".[dev]"
```
from inside a virtual environment (use either venv or anaconda). This will import VolFe
in a format that allows you to run any edits you have made, and all it's requirements,
alongside useful packages for developing VolFe (pytest, sympy).

Check VolFe runs on your machine, and that any edits you make haven't broken existing code by running pytest:
```
python -m pytest tests
```
or you can use the testing frameworks that come with your IDE (e.g. [VSCode](https://code.visualstudio.com/docs/python/testing), [PyCharm](https://www.jetbrains.com/help/pycharm/testing-your-first-python-application.html)).