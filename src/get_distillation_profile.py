import requests
from bs4 import BeautifulSoup
import re
import pandas as pd
import numpy as np


def get_distillation_profile(crude_name, date="recent"):
    """
    Retrieve distillation profile of specified crude
    from https://crudemonitor.ca/home.php.
    
    Arguments:
    ----------
    crude_name : str
        acronym of crude
    date : str
        Date for which to get distillation profile.
        Must be in format 'YYYY-MM-DD' or 'recent'.
        Defaults to 'recent'.
        
    Returns:
    --------
    pandas.DataFrame
        Dataframe storing distillation profile of specified crude.
        
    Examples:
    ---------
    >>> crude = "MGS"
    >>> date = "recent"
    >>> get_distillation_profile(crude, date)
    """

    assert date == "recent" or re.match("\\d\\d\\d\\d-\\d\\d-\\d\\d", date), \
        "date must be either 'recent' or in format YYYY-MM-DD"

    webpage = f"https://crudemonitor.ca/crudes/dist.php?"
    params = f"acr={crude_name}&time={date}"
    distillation_data = requests.get(webpage + params)
    soup = BeautifulSoup(distillation_data.text, "lxml")

    err_msg1 = "No crudes match the given acronym."
    if soup.text[-34:] == err_msg1:
        print(f"No distillation samples available for specified crude '{crude_name}'.")
        return

    err_msg2 = "No distillation samples available."
    if soup.text[-34:] == err_msg2:
        print("No distillation samples available for specified date.")
        return

    class_name = {"class" : "table table-sm table-striped"}
    for table in soup.find_all("table", class_name):

        for th in table.find_all("tr", {"id" : "tableHeadRow"}):
            headers = re.findall("[^\n]*" , th.text)

        row_list = []
        index_list = []
        for tr in table.find_all("tr"):
            row = []
            for td in tr.find_all("td"):
                row.append(td.text.replace(",", ""))
            row_list.append(row)

            for th in tr.find_all("th"):
                index = th.text
            index_list.append(index)

    if headers is not None:
        headers = [x for x in headers if x != ""]
    
    dp_df = pd.DataFrame(data=row_list[1:], 
                         columns=headers[1:], 
                         index=index_list[1:])
    
    celsius_cols = ["Temperature( oC )", 
                    "Average( oC )",
                    "Standard Deviation( oC )"]
    return dp_df.replace("-", np.nan).astype(float)[celsius_cols]
