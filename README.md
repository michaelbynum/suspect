Special Structure Detection for Pyomo
=====================================

[![DOI](https://zenodo.org/badge/127118649.svg)](https://zenodo.org/badge/latestdoi/127118649) [![Build Status](https://travis-ci.org/cog-imperial/suspect.svg?branch=master)](https://travis-ci.org/cog-imperial/suspect) [![codecov](https://codecov.io/gh/cog-imperial/suspect/branch/master/graph/badge.svg)](https://codecov.io/gh/cog-imperial/suspect)


This library implements methods to:

* Detect convex and concave expressions
* Detect increasing and decreasing expressions
* Detect linear, quadratic and polynomial expressions
* Tighten expression bounds


Documentation
-------------

Documentation is available at https://cog-imperial.github.io/suspect/


Installation
------------

SUSPECT requires Python 3.5 or later. We recommend installing SUSPECT in
a virtual environment

To create the virtual environment run:

    $ python3 -m venv myenv
    $ source myenv/bin/activate

Then you are ready to clone and install SUSPECT

    $ git clone https://github.com/cog-imperial/suspect.git
    $ cd suspect
    $ pip install -r requirements.txt
    $ pip install .


Command Line Usage
------------------

The package contains an utility to display structure information about
a single problem.

You can run the utility as:

    model_summary.py -p /path/to/problem.osil

or, if you want to check variables bounds include the solution:

    model_summary.py -p /path/to/problem.osil -s /path/to/problem.sol

The repository also includes a `Dockerfile` to simplify running the utility in
batch mode in a cloud environment. Refer to the `batch` folder for more information.


Library Usage
-------------

    from suspect import (
	    set_pyomo4_expression_tree,
	    detect_special_structure,
    )
    import pyomo.environ as aml


    set_pyomo4_expression_tree()


    model = aml.ConcreteModel()
    model.x = aml.Var()
    model.y = aml.Var()

    model.obj = aml.Objective(expr=(model.y - model.x)**3)
    model.c1 = aml.Constraint(expr=model.y - model.x >= 0)

    info = detect_special_structure(model)

    # try info.variables, info.objectives, and info.constraints
    print(info.objectives['obj'])


License
-------

Copyright 2018 Francesco Ceccon

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
