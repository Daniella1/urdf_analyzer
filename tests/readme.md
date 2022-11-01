To run a unittest, you can do this from the root directory of the repository, and run `python -m unittest tests.test_filename`. 

For example if you want to run the api tests, you can run `python -m unittest tests.test_api`.

To run all the tests, run `python -m unittest discover tests`. The last argument `tests` specifies the directory to look for the tests.


To check the code coverage, make sure `coverage` is installed, and from the root directory of the repository, run `coverage run -m unittest discover`, to generate the coverage report.
To view the coverage report, run `coverage report`.