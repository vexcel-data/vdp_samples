## Introduction

This repository is primarily aimed to get Vexcel Data Program customers, and GIC members up and running with Vexcel products by providing code examples in Python and Javascript that utilize our API. For those without an existing subscription or evaluation license, get in touch at https://vexceldata.com/request-a-demo/ to request an evaluation with less limiations.

## How to use this repo

There are 4 main folders in this repository:
- scripts: python scripts that carry out a specific function created mostly for their utility, to either make it easier for a customer to use our data or for us to carry out common analyses
- notebooks: python notebooks that show customers how to use our products. While they're useful, their format lends itself to being a way of educating customers and this is this folders primary distinction from the scripts folder
- vpd_python_tools: a place for functions that are generic enough to be used across at least 2 scripts or notebooks. If you find yourself copynig a function from one script/notebook to another, consider adding it to vdp_python_tools and importing from there
- web: a place for small client side web apps. For more information on each app, please address the README.md
    ```
    vdp_python_tools_and_snippets/
      web/
        time_slider
        AuthenticationDemoApp
        ...
    ```

In order to use this repo effectively, you'll need to install vdp_python_tools (see section below). Following those instructions will install everything you need to run the notebooks and scripts (explained further down).

### Installing vdp_python_tools

0. Clone this repo
1. Download latest version of Python - https://www.python.org/downloads/
2. Make sure you have Anaconda which is a handy package manager for Python. It's more powerful than pip as it will take care of tricky libraries like GDAL. To get Anaconda, head to https://docs.conda.io/en/latest/miniconda.html to learn how to get that installed
3. From within this folder (at the same level as this README.md) run `conda env create -f environment.yml` to install all of the necessary libraries based on the supplied environment.yml. It will create an environment named `vdp_python_tools`
4. Run `conda activate vdp_python_tools`
5. Run `pip install .`
6. The best way to handle authentication is to have your user credentials stored as environment variables. You could pass your username and password to the authentication function each time, but it's easier and more secure to avoid placing your credentials in code and just use environment variables. Add your password e.g "aReallyGoodPassword123" to an environment variable called `VDP_PASSWORD` and your email e.g my@email.com to `VDP_USERNAME`. (This article https://dev.to/pizofreude/environment-variables-a-comprehensive-guide-34dg does a great job of explaining how to set environment variables on Windows, Linux or OSX. Don't forget that you'll need to create a new terminal, as the environment variables won't be defined until the terminal restarts (or, run `source ~/.bashrc` or `source ~/.bash_profile` depending on where you saved those variables).
7. If everything ran without an error, you should be able to run the following:
   1. `python`
   2. (from within the python console) `from vdp_python_tools.authentication import login; login()` and that should print a long string of random letters and numbers which is your authentication token! The Python notebooks in notebooks/basic explain how to use this token to get data back from the API.d 

For more information on the functions within vdp_python_tools, see the section further down.

### Using the Jupyter notebooks

Jupyter (Julia + Python) allows you to view Python code (and other supported languages) in a notebook format where you can write code in a series of cells and observe the output from functions before moving to the next step in your workflow. It's a great way to explore the pieces in a data pipeline before packaging it all up into a script or a new function.

Jupyter was installed automatically in the steps above. To use Jupyter, simply run `jupyter notebook` on the command line. This will output something like:
```
[I 10:37:29.914 NotebookApp] Serving notebooks from local directory: /Users/patrick/Projects/vdp_python_tools_and_snippets/vdp_python_tools
[I 10:37:29.914 NotebookApp] Jupyter Notebook 6.4.5 is running at:
[I 10:37:29.914 NotebookApp] http://localhost:8888/?token=24153bb382ae5055d4316874bb489ef6cd8b02ec444ab66e
[I 10:37:29.915 NotebookApp]  or http://127.0.0.1:8888/?token=24153bb382ae5055d4316874bb489ef6cd8b02ec444ab66e
[I 10:37:29.915 NotebookApp] Use Control-C to stop this server and shut down all kernels (twice to skip confirmation).
```
Typically your web browser will automatically have a new tab opened at http://localhost:8888. If it doesn't, navigate there yourself. You'll need to add the token which is printed into the output above and will change each time you run Jupyter.

If you run `jupyter notebook` from the top of this repo, you'll see a file explorer with a list of folders including notebooks. You can navigate into folders to view the text format of each file but notebooks will open in their notebook format.


## Getting updates

Whenever this repository is updated, we'll make a note of the changes and how to make sure you can continue using the scripts, modules and notebooks such as whether to update your Anaconda environment. 

## Installing PostGIS

`
-- Enable PostGIS (as of 3.0 contains just geometry/geography)
CREATE EXTENSION postgis;
-- enable raster support (for 3+)
CREATE EXTENSION postgis_raster;
-- Enable Topology
CREATE EXTENSION postgis_topology;
-- Enable PostGIS Advanced 3D
-- and other geoprocessing algorithms
-- sfcgal not available with all distributions
CREATE EXTENSION postgis_sfcgal;
-- fuzzy matching needed for Tiger
CREATE EXTENSION fuzzystrmatch;
-- rule based standardizer
CREATE EXTENSION address_standardizer;
-- example rule data set
CREATE EXTENSION address_standardizer_data_us;
-- Enable US Tiger Geocoder
CREATE EXTENSION postgis_tiger_geocoder;
`
