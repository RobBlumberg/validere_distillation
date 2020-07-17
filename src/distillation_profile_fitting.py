import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import scipy.stats
from scipy.optimize import curve_fit
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
    ax : matplotlib.axes._subplots.AxesSubplot
        object on which to plot fit results
    date : str
        Date for which to get distillation profile.
        Must be in format 'YYYY-MM-DD' or 'recent'.
        Defaults to 'recent'.
        
    Returns:
    --------
    tuple : (numpy.ndarray, numpy.ndarray, numpy.ndarray, 
             matplotlib.axes._subplots.AxesSubplot)
        - Fit parameters from scipy.optimize.curve_fit.
        - Covariance matrix from scipy.optimize.curve_fit.
        - Values which define fit curve.
        - Matplotlib object on which fitted curve is plotted.
    
        
    Examples:
    ---------
    >>> crude = "MGS"
    >>> date = "recent"
    >>> fig, ax = plt.subplots(1, 1, figsize=(10, 6))
    >>> get_distillation_profile(crude, ax, date)
    """
    
    crude_df = get_distillation_profile(crude_name, date=date)
    temp = crude_df["Temperature( oC )"].dropna()
    distilled = [float(x) / 100 if x != "IBP" else 0 for x in list(crude_df.index)][0:len(temp)]

    f = lambda temp, a, b: scipy.stats.gamma(a=a, scale=b).cdf(temp)
    fit_params, cov_matrix = curve_fit(f, temp, distilled, p0=[5, 60])
    
    temps = np.linspace(0, max(temp), 1000)
    fit_vals = scipy.stats.gamma(a=fit_params[0], scale=fit_params[1]).cdf(temps)
    
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
        - DataFrame storing distillation profile of mixtue
        - Matplotlib object on which fitted curves are plotted.
    """
    assert vol1 >=0 and vol2 >=0, \
        "Specified volumues 'vol1' and 'vol2' must be positive."
    
    crude1_df = get_distillation_profile(crude1)
    crude2_df = get_distillation_profile(crude2)

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
    
    total_vol = vol1 + vol2
    
    temps = np.linspace(0, 1000, 1000)
    mixture_model = (vol1 / total_vol)*scipy.stats.gamma(a=fit_params1[0], scale=fit_params1[1]).cdf(temps) + \
                    (vol2 / total_vol)*scipy.stats.gamma(a=fit_params2[0], scale=fit_params2[1]).cdf(temps)

    ax[2].plot(temps, mixture_model, color="red")
    ax[2].set_xlabel("Temperature (oC)", size=16)
    ax[2].set_ylabel("Mass % Recovered", size=16)
    ax[2].tick_params(labelsize=16)
    ax[2].annotate(f"Gamma mixture model: \n" + 
                   "---------------------------\n" +
                   f"{vol1 / total_vol :.2f} F({crude1}) + \n{vol2 / total_vol :.2f} F({crude2})", 
                   xy=(0, 0.75), 
                   size=16)
    ax[2].set_title("Crude Mixture Distillation Profile", size=16)
    ax[2].set_ylim(-0.05, 1)
    
    distilliation_percentages = [0.05] + [0.1*x for x in range(1, 10)] + [0.95 + 0.99]
    temps = [np.absolute(mixture_model - x).argmin()-1 for x in distilliation_percentages]
    
    mixture_distillation_profile_df = pd.DataFrame({"Mass % Recovered" : distilliation_percentages,
                                                    "Temperature (oC)" : temps})
        
    return mixture_distillation_profile_df, fig
