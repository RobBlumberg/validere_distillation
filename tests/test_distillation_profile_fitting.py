from src.get_distillation_profile import get_distillation_profile
from src.distillation_profile_fitting import gamma_fit, gamma_mixture_distillation_profile
import matplotlib
import matplotlib.pyplot as plt


def test_gamma_fit_params():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    fit_params, cov_matrix, fit_vals, ax = gamma_fit("RA", ax, "recent")

    assert fit_params.shape == (2, ), \
        "Function should return 2 fit parameters"


def test_gamma_fit_cov_matrix():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    fit_params, cov_matrix, fit_vals, ax = gamma_fit("RA", ax, "recent")

    assert cov_matrix.shape == (2, 2), \
        "Function should return a 2x2 covariance maxtrix for fit parameters"


def test_gamma_fit_vals():
    fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    fit_params, cov_matrix, fit_vals, ax = gamma_fit("RA", ax, "recent")

    assert fit_vals.shape == (1000, ), \
        "Function should return 1000 fit values."


def test_gamma_mixture_df():
    crude1 = "MGS"
    crude2 = "RA"
    vol1 = 10
    vol2 = 5
    results = gamma_mixture_distillation_profile(crude1, crude2, vol1, vol2)

    assert results[0].shape == (11, 2), \
        "Function should return a data frame of shape 13x2."


def test_gamma_mixture_plot():
    crude1 = "MGS"
    crude2 = "RA"
    vol1 = 10
    vol2 = 5
    results = gamma_mixture_distillation_profile(crude1, crude2, vol1, vol2)

    assert isinstance(results[1], matplotlib.figure.Figure), \
        "Function should return correct matplotlib object."
