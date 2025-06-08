# divisional.py

def get_absolute_degree(sign, degree_in_sign):
    """Returns the absolute zodiac degree from sign index (0-11) and degree."""
    return sign * 30 + degree_in_sign

def get_d3_chart(planets_d1, asc_deg):
    chart = {}
    for key, deg in planets_d1.items():
        d3_sign = (int(deg // 10) % 12) + 1
        chart[key] = d3_sign
    chart['Ascendant'] = (int(asc_deg // 10) % 12) + 1
    return chart

def get_d9_chart(planets_d1, asc_deg):
    chart = {}
    for key, deg in planets_d1.items():
        d9_sign = ((int(deg * 9 // 30)) % 12) + 1
        chart[key] = d9_sign
    chart['Ascendant'] = ((int(asc_deg * 9 // 30)) % 12) + 1
    return chart

def get_d6_chart(planets_d1, asc_deg):
    chart = {}
    for key, deg in planets_d1.items():
        d6_sign = ((int(deg * 6 // 30)) % 12) + 1
        chart[key] = d6_sign
    chart['Ascendant'] = ((int(asc_deg * 6 // 30)) % 12) + 1
    return chart

def get_d30_chart(planets_d1, asc_deg):
    chart = {}
    for key, deg in planets_d1.items():
        d30_sign = ((int(deg * 30 // 30)) % 12) + 1
        chart[key] = d30_sign
    chart['Ascendant'] = ((int(asc_deg * 30 // 30)) % 12) + 1
    return chart

def get_d60_chart(planets_d1, asc_deg):
    chart = {}
    for key, deg in planets_d1.items():
        d60_sign = ((int(deg * 60 // 30)) % 12) + 1
        chart[key] = d60_sign
    chart['Ascendant'] = ((int(asc_deg * 60 // 30)) % 12) + 1
    return chart
