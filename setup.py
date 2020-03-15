from setuptools import setup

setup(
    name="FreeComet",
    version="1.0.0",
    description="FreeComet application.",
    long_description=README,
    long_description_content_type="text/markdown",
    url="https://github.com/dsuarezgarcia/freecomet",
    author="Diego Suárez",
    author_email="d.suarez@udc.es",
    license="MIT",
    classifiers=[
        "License :: OSI Approved :: MIT License",
        "Programming Language :: Python",
        "Programming Language :: Python :: 2",
        "Programming Language :: Python :: 3",
    ],
    packages=["sample"],
    include_package_data=True,
    install_requires=[
        "OpenCV", "NumPy", "scikit-image", "scikit-learn", "pathvalidate", "xlwt", "cairo", "GTK3"
    ],
    entry_points={"console_scripts": ["realpython=sample.__main__:main"]},
)