import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from scipy.optimize import curve_fit
import sys
sys.path.insert(0, "src")
from get_distillation_profile import get_distillation_profile


def gamma_fit(crude_name, ax, date="recent"):
    """
    Fit a gamma CDF to a specified crude oil's
    distillation profile data from
    https://crudemonitor.ca/home.php.

    Arguments:
    ----------
    crude_name : str
        acronym of crude
    ax : matplotlib.axes.Axes
        object on which to plot fit results
    date : str
        Date for which to get distillation profile.
        Must be in format 'YYYY-MM-DD' or 'recent'.
        Defaults to 'recent'.

    Returns:
    --------
    tuple : (numpy.ndarray, numpy.ndarray, numpy.ndarray,
             matplotlib.axes.Axes)
        - Fit parameters from scipy.optimize.curve_fit.
        - Covariance matrix from scipy.optimize.curve_fit.
        - Values which define fit curve.
        - Matplotlib object on which fitted curve is plotted.

    Examples:
    ---------
    >>> from distillation_profile_fitting import gamma_fit
    >>> import matplotlib.pyplot as plt
    >>> crude = "MGS"
    >>> date = "recent"
    >>> fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    >>> gamma_fit(crude, ax, date)
    """
    # get crude's distillation profile data
    crude_df = get_distillation_profile(crude_name, date=date)
    if crude_df is None:
        return

    # remove nan's and convert to float
    temp = crude_df["Temperature( oC )"].dropna()
    distilled = [float(x) / 100 if x != "IBP" else 0
                 for x in list(crude_df.index)][0:len(temp)]

    # fit gamma CDF
    f = lambda temp, a, b: scipy.stats.gamma(a=a, scale=b).cdf(temp)
    fit_params, cov_matrix = curve_fit(f, temp, distilled, p0=[5, 60])

    temps = np.linspace(0, max(temp), 1000)
    fit_vals = scipy.stats.gamma(a=fit_params[0],
                                 scale=fit_params[1]).cdf(temps)

    # plot results
    ax.scatter(temp, distilled)
    ax.plot(temps, fit_vals, color="red")
    ax.set_xlabel("Temperature (oC)", size=16)
    ax.set_ylabel("Mass % Recovered", size=16)
    ax.tick_params(labelsize=16)
    ax.annotate(f"Gamma fit params: \n" +
                "---------------------------\n" +
                f"alpha : {fit_params[0]:.3f}\nbeta : {fit_params[1]:.3f}",
                xy=(0, 0.75),
                size=16)
    ax.set_ylim(-0.05, 1)

    return fit_params, cov_matrix, fit_vals, ax


def gamma_mixture_distillation_profile(crude1, crude2, vol1, vol2):
    """
    Calculates a gamma mixture model by fitting separate gamma CDFs
    to each specified crude's distillation profile, and using
    specified volumes as proportions.

    Arguments:
    ----------
    crude1 : str
        Acronym of first crude in mixture
    crude2 : str
        Acronym of second crude in mixture
    vol1 : float
        Volume of first crude in mixture.
        Must be positive.
        Units unimportant as this argument is simply
        used to calculate a proportion.
    vol2 : float
        Volume of second crude in mixture.
        Must be positive.
        Units unimportant as this argument is simply
        used to calculate a proportion.

    Returns:
    --------
    tuple : (pandas.DataFrame, matplotlib.figure.Figure)
        - DataFrame storing distillation profile of mixture
        - Matplotlib object on which fitted curves are plotted.

    Examples:
    ---------
    >>> from distillation_profile_fitting import gamma_mixture_distillation_profile
    >>> crude1 = "MGS"
    >>> crude2 = "RA"
    >>> vol1 = 10
    >>> vol2 = 5
    >>> gamma_mixture_distillation_profile(crude1, crude2, vol1, vol2)
    """
    assert vol1 >= 0 and vol2 >= 0, \
        "Specified volumes 'vol1' and 'vol2' must be positive."

    # fit gamma CDF to each crude
    fig, ax = plt.subplots(1, 3, figsize=(20, 6))
    try:
        fit_params1, cov_matrix1, fit_vals1, ax1 = gamma_fit(crude1, ax[0])
    except TypeError:
        return
    ax[0].set_title(f"Crude 1 : {crude1} (Vol={vol1})", size=16)

    try:
        fit_params2, cov_matrix2, fit_vals2, ax2 = gamma_fit(crude2, ax[1])
    except TypeError:
        return
    ax[1].set_title(f"Crude 2 : {crude2} (Vol={vol2})", size=16)

    # create gamma mixture model using volumes and CDFs
    total_vol = vol1 + vol2
    temps = np.linspace(0, 1000, 1000)
    mixture_model = ((vol1 / total_vol)*scipy.stats.gamma(a=fit_params1[0],
                                                          scale=fit_params1[1])
                                                   .cdf(temps)) + \
                    ((vol2 / total_vol)*scipy.stats.gamma(a=fit_params2[0],
                                                          scale=fit_params2[1])
                                                   .cdf(temps))

    # plot results
    ax[2].plot(temps, mixture_model, color="red")
    ax[2].set_xlabel("Temperature (oC)", size=16)
    ax[2].set_ylabel("Mass % Recovered", size=16)
    ax[2].tick_params(labelsize=16)
    ax[2].annotate(f"Gamma mixture model: \n" +
                   "---------------------------\n" +
                   f"{vol1 / total_vol :.2f} x F({crude1}) + " +
                   f"\n{vol2 / total_vol :.2f} x F({crude2})",
                   xy=(0, 0.75),
                   size=16)
    ax[2].set_title("Crude Mixture Distillation Profile", size=16)
    ax[2].set_ylim(-0.05, 1)

    # determine temperature values at relevant remaining mass percentages
    distilliation_percentages = [0.05] + \
                                [0.1*x for x in range(1, 10)] + \
                                [0.95, 0.99]
    temps = [np.absolute(mixture_model - x).argmin()-1
             for x in distilliation_percentages]

    mix_dist_df = pd.DataFrame({"Mass % Recovered": distilliation_percentages,
                                "Temperature (oC)": temps})

    return mix_dist_df, fig
