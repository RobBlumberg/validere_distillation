from src.get_distillation_profile import get_distillation_profile


def test_invalid_crude():
    crude = "ABC"
    date = "recent"
    dp = get_distillation_profile(crude, date)

    assert dp is None, \
        "Function should not return anything for invalid crude acronym."


def test_invalid_date():
    crude = "RA"
    date = "01-01-01"
    try:
        dp = get_distillation_profile(crude, date)
    except AssertionError:
        print("Function should throw assertion error for invalid date.")


def test_valid_crude():
    crude = "RA"
    date = "recent"
    dp_df = get_distillation_profile(crude, date)

    assert dp_df.shape == (13, 3), \
        "Function should return a data frame of shape 13x3."


def test_date():
    crude = "RA"
    date = "2020-06-10"
    dp_df = get_distillation_profile(crude, date)

    assert dp_df.shape == (13, 3), \
        "Function should return a data frame of shape 13x3."
