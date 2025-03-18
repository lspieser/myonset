"""
This file is part of Myonset.

Myonset is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

Myonset is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with Myonset. If not, see <https://www.gnu.org/licenses/>.
"""    
import setuptools


with open("README.md", "r") as fh:
    long_description = fh.read()
    
setuptools.setup(
        name = "myonset",
        version = "1.0",
        author = "Laure Spieser and Boris Burle",
        author_email = "laure.spieser@univ-amu.fr",
        description = "Myonset is a package for detecting EMG burst onset.",
        long_description = long_description,
        long_description_content_type = "text/markdown",
		keywords = "EMG electromyography",
		license = "GNU GPLv3",
        url = "",
        packages = setuptools.find_packages(),
		install_requires = ["pyqtgraph"],
        classifiers = [
                "Programming Language :: Python :: 3",
                "Topic :: Scientific/Engineering :: Medical Science Apps.",
                "License :: OSI Approved :: GNU General Public License v3 (GPLv3)",
                "Operating System :: OS Independent",
                ],
        python_requires = '>=3.6',
        )


