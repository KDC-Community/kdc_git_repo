'''tzinfo timezone information for America/Miquelon.'''
from pytz.tzinfo import DstTzInfo
from pytz.tzinfo import memorized_datetime as d
from pytz.tzinfo import memorized_ttinfo as i

class Miquelon(DstTzInfo):
    '''America/Miquelon timezone definition. See datetime.tzinfo for details'''

    zone = 'America/Miquelon'

    _utc_transition_times = [
d(1,1,1,0,0,0),
d(1911,5,15,3,44,40),
d(1980,5,1,4,0,0),
d(1987,4,5,5,0,0),
d(1987,10,25,4,0,0),
d(1988,4,3,5,0,0),
d(1988,10,30,4,0,0),
d(1989,4,2,5,0,0),
d(1989,10,29,4,0,0),
d(1990,4,1,5,0,0),
d(1990,10,28,4,0,0),
d(1991,4,7,5,0,0),
d(1991,10,27,4,0,0),
d(1992,4,5,5,0,0),
d(1992,10,25,4,0,0),
d(1993,4,4,5,0,0),
d(1993,10,31,4,0,0),
d(1994,4,3,5,0,0),
d(1994,10,30,4,0,0),
d(1995,4,2,5,0,0),
d(1995,10,29,4,0,0),
d(1996,4,7,5,0,0),
d(1996,10,27,4,0,0),
d(1997,4,6,5,0,0),
d(1997,10,26,4,0,0),
d(1998,4,5,5,0,0),
d(1998,10,25,4,0,0),
d(1999,4,4,5,0,0),
d(1999,10,31,4,0,0),
d(2000,4,2,5,0,0),
d(2000,10,29,4,0,0),
d(2001,4,1,5,0,0),
d(2001,10,28,4,0,0),
d(2002,4,7,5,0,0),
d(2002,10,27,4,0,0),
d(2003,4,6,5,0,0),
d(2003,10,26,4,0,0),
d(2004,4,4,5,0,0),
d(2004,10,31,4,0,0),
d(2005,4,3,5,0,0),
d(2005,10,30,4,0,0),
d(2006,4,2,5,0,0),
d(2006,10,29,4,0,0),
d(2007,4,1,5,0,0),
d(2007,10,28,4,0,0),
d(2008,4,6,5,0,0),
d(2008,10,26,4,0,0),
d(2009,4,5,5,0,0),
d(2009,10,25,4,0,0),
d(2010,4,4,5,0,0),
d(2010,10,31,4,0,0),
d(2011,4,3,5,0,0),
d(2011,10,30,4,0,0),
d(2012,4,1,5,0,0),
d(2012,10,28,4,0,0),
d(2013,4,7,5,0,0),
d(2013,10,27,4,0,0),
d(2014,4,6,5,0,0),
d(2014,10,26,4,0,0),
d(2015,4,5,5,0,0),
d(2015,10,25,4,0,0),
d(2016,4,3,5,0,0),
d(2016,10,30,4,0,0),
d(2017,4,2,5,0,0),
d(2017,10,29,4,0,0),
d(2018,4,1,5,0,0),
d(2018,10,28,4,0,0),
d(2019,4,7,5,0,0),
d(2019,10,27,4,0,0),
d(2020,4,5,5,0,0),
d(2020,10,25,4,0,0),
d(2021,4,4,5,0,0),
d(2021,10,31,4,0,0),
d(2022,4,3,5,0,0),
d(2022,10,30,4,0,0),
d(2023,4,2,5,0,0),
d(2023,10,29,4,0,0),
d(2024,4,7,5,0,0),
d(2024,10,27,4,0,0),
d(2025,4,6,5,0,0),
d(2025,10,26,4,0,0),
d(2026,4,5,5,0,0),
d(2026,10,25,4,0,0),
d(2027,4,4,5,0,0),
d(2027,10,31,4,0,0),
d(2028,4,2,5,0,0),
d(2028,10,29,4,0,0),
d(2029,4,1,5,0,0),
d(2029,10,28,4,0,0),
d(2030,4,7,5,0,0),
d(2030,10,27,4,0,0),
d(2031,4,6,5,0,0),
d(2031,10,26,4,0,0),
d(2032,4,4,5,0,0),
d(2032,10,31,4,0,0),
d(2033,4,3,5,0,0),
d(2033,10,30,4,0,0),
d(2034,4,2,5,0,0),
d(2034,10,29,4,0,0),
d(2035,4,1,5,0,0),
d(2035,10,28,4,0,0),
d(2036,4,6,5,0,0),
d(2036,10,26,4,0,0),
d(2037,4,5,5,0,0),
d(2037,10,25,4,0,0),
        ]

    _transition_info = [
i(-13500,0,'LMT'),
i(-14400,0,'AST'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
i(-7200,3600,'PMDT'),
i(-10800,0,'PMST'),
        ]

Miquelon = Miquelon()
