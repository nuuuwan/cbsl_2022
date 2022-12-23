class FREQUENCY:
    ANNUALLY = 'annually'
    CENSUS_YEAR = 'census-year'
    ACADEMIC_YEAR = 'academic-year'
    HALF_YEARLY = 'half-yearly'
    QUARTERLY = 'quarterly'
    MONTHLY = 'monthly'
    DAILY = 'daily'


TIME_WINDOW_YEARS = 100


def build_frequency_config():
    return {
        FREQUENCY.ANNUALLY: {
            'time_span': ['1925', '2025'],
        },
        FREQUENCY.CENSUS_YEAR: {
            'time_span': ['1925', '2025'],
        },
        FREQUENCY.ACADEMIC_YEAR: {
            'time_span': ['1925', '2025'],
        },
        FREQUENCY.HALF_YEARLY: {
            'time_span': ['1925', '2025'],
        },
        FREQUENCY.QUARTERLY: {
            'time_span': ['1925', '2025'],
        },
        FREQUENCY.MONTHLY: {
            'time_span': ['1925-01', '2025-01'],
        },
        FREQUENCY.DAILY: {
            'time_span': ['1925-01-01', '2025-01-01'],
        },
    }


FREQUENCY_CONFIG = build_frequency_config()
