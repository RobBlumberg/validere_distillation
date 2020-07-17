# Distillation Profile of a Blend of Crude Oils

This repository contains a model which calculates the distillation profile of a blend of two crude oils, given their individual distillation profiles. The code which implements the modelling can be found in the `distillation_profile_fitting.py` script in the `src` directory. Also in the `src` directory is a script called `get_distillation_profile.py`, which allows fetching of the distillation profile data from https://crudemonitor.ca/. A walkthrough of the modelling is performed in the [`distillation-profile.ipynb` notebook](https://github.com/RobBlumberg/validere_distillation/blob/master/src/distillation-profile.ipynb), which is also in the `src` directory.

## Modelling Explanation and Assumptions

Previous research (See [here](https://digital.library.adelaide.edu.au/dspace/bitstream/2440/88659/8/02whole.pdf) - reference Riazi 2005) has shown that a Gamma CDF can be used to model the relationship between temperature and the percentage of evaporated crude oil. Thus, we can fit a Gamma CDF to a crude oil's distillation profile data to obtain its distillation profile curve in functional form. 

Two separate regressions can be performed on two separate crude oils to yield two distillation profile curves. If these two crudes are then mixed, we can simply sum the individial gamma distributions, weighted by the volumes of each oil in the mixture, to obtain a gamma mixture model, which represents the distillation curve of the crude mixture.

The main assumption made by this model is that the molecules from each crude evaporate under the same probabilistic distributions as they did when unmixed.

A more detailed explanation of the modelling and assumptions can be found in the [`distillation-profile.ipynb` notebook](https://github.com/RobBlumberg/validere_distillation/blob/master/src/distillation-profile.ipynb).

## Usage

**get_distillation_profile**

The `get_distillation_profile` function takes a crude acronym (See [here](https://crudemonitor.ca/home.php) for possible acronyms) and a date (defaults to 'recent', where most recent date is taken). It returns a pandas dataframe storing the distillation curve for the specified crude and date.

```python
>>> from get_distillation_profile import get_distillation_profile
>>> crude = "MGS"
>>> date = "recent"
>>> get_distillation_profile(crude, date)
```

**gamma_fit**

The `gamma_fit` function fits a gamma CDF to a specified crude oil's distillation profile data from https://crudemonitor.ca/home.php. The function calls `get_distillation_profile` internally, and so the fit can be performed directly without calling any other function, as shown below. It is necessary to pass in a matplotlib `ax` object on which the results are plotted.

```python
>>> from distillation_profile_fitting import gamma_fit
>>> fig, ax = plt.subplots(1, 1, figsize=(10, 6))
>>> results = gamma_fit("RA", ax, date="recent");
```

**gamma_mixture_distillation_profile**

The `gamma_mixture_distillation_profile` function fits a gamma CDF to each specified crude oil's distillation profile data from https://crudemonitor.ca/home.php. Again, the function calls `get_distillation_profile` internally on each specified crude, and so the fitting can be performed directly without calling any other function. Once the individual crudes are fit, the function performs a weighted sum of the gamma CDFs using the specified volumes of each crude to yield the gamma mixture model for the crude oil mixture.

```python
>>> from distillation_profile_fitting import gamma_mixture_distillation_profile
>>> crude1 = "MGS"
>>> crude2 = "RA"
>>> vol1 = 10
>>> vol2 = 5
>>> gamma_mixture_distillation_profile(crude1, crude2, vol1, vol2)
```

## Tests

To test the functions, call `python -m pytest tests/` from the root of this repository.







