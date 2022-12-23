from utils import timex


class FREQUNCY:
    ANNUALLY = 'annually'
    CENSUS_YEAR = 'census-year'
    ACADEMIC_YEAR = 'academic-year'
    HALF_YEARLY = 'half-yearly'
    QUARTERY = 'quarterly'
    MONTHLY = 'monthly'
    DAILY = 'daily'


TIME_WINDOW_YEARS = 100


def build_frequency_config():
    max_ut = timex.get_unixtime()
    min_ut = max_ut - timex.SECONDS_IN.YEAR * TIME_WINDOW_YEARS

    # min_date, max_date = list(map(
    #     lambda ut: timex.format_time(ut, '%Y-%m-%d'),
    #     [min_ut, max_ut],
    # ))

    min_month, max_month = list(
        map(
            lambda ut: timex.format_time(ut, '%Y-%m'),
            [min_ut, max_ut],
        )
    )

    min_year, max_year = list(
        map(
            lambda ut: timex.format_time(ut, '%Y'),
            [min_ut, max_ut],
        )
    )

    return {
        FREQUNCY.ANNUALLY: {
            'time_span': [min_year, max_year],
        },
        FREQUNCY.MONTHLY: {
            'time_span': [min_month, max_month],
        },
        # FREQUNCY.DAILY: {
        #     'time_span': [min_date, max_date],
        # },
    }


FREQUNCY_CONFIG = build_frequency_config()
