## Introduction

This folder contains a set of Jupyter notebooks that provide code examples in Python. Displaying the examples in Jupyter allows readers to go through the steps of a solution while executing code as they go, while visualising the intemediary data.

For instructions on how to get started with theses notebooks see the "Installing vdp_python_tools" and "Using the Jupyter notebooks" sections in the README.md located in the folder above.

## Basics

Most users of the API will need to understand the concepts introduced in these notebooks.

- 0. An introduction to WMTS in Python: this is aimed at those without any knowledge of how map tiles work, as well as a limited understanding of Python. 
- 1. Getting started: A minimal set of exampels on how to use the VDP APIs in Python
- 2. Checking coverage with the API: it's important to know where our data is available, the type of data, and when it was captured. This notebook covers how to determine all of that and visualise it, before showing how you can use that information to make more targeted requests for imagery

## Advanced

This set of notebooks showcase a range of solutions to common problems that users of VDP data are trying to solve.

- Simple algorithms on DSM and RGB imagery: shows how the DSM can be segmented using simple clustering algorithms to detect features in an unsupervised manner and map the results from the reference frame of an image to the earth
- Pulling tiles for a large area: in cases where the ExtractOrthoImages API isn't appropriate, this notebook introduces strategies for aquiring tiles over a large area, georeferencing them, and then creating a mosaic in an arbitrary CRS
- Point cloud creation: some users of our elevation products are more familiar with point clouds and this notebook shows how to transform our DSM and Ortho tiles in LAS files
- Create world files ExtractOrthoImages: when using the ExtractOrthoImage API, it can be useful to obtain a 'World file' that provides the location of that image on the world. This notebook takes a first principles approach to doing this that - while is implemented in Python - can be adapted to other languages as it doesn't rely on libraries like Shapely or Rasterio that only exist in Python


