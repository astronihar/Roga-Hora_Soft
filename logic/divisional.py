def get_absolute_degree(sign_index, degree_in_sign):
    return sign_index * 30 + degree_in_sign

def get_sign_and_degree(absolute_deg):
    sign = int(absolute_deg // 30)
    degree_in_sign = absolute_deg % 30
    return sign, degree_in_sign

def get_d1_chart(planets_raw, asc_deg):
    chart = {**planets_raw}
    chart['Ascendant'] = int(asc_deg // 30) + 1
    return chart

def get_d3_chart(planets_raw, asc_deg):
    chart = {}
    for planet, abs_deg in planets_raw.items():
        sign, deg = get_sign_and_degree(abs_deg)
        drekkana = int(deg // 10)
        if drekkana == 0:
            final_sign = sign
        elif drekkana == 1:
            final_sign = (sign + 5) % 12
        else:
            final_sign = (sign + 9) % 12
        chart[planet] = final_sign + 1
    # Ascendant
    sign, deg = get_sign_and_degree(asc_deg)
    drekkana = int(deg // 10)
    if drekkana == 0:
        final_sign = sign
    elif drekkana == 1:
        final_sign = (sign + 5) % 12
    else:
        final_sign = (sign + 9) % 12
    chart['Ascendant'] = final_sign + 1
    return chart

def get_d6_chart(planets_raw, asc_deg):
    chart = {}
    for planet, abs_deg in planets_raw.items():
        sign, deg = get_sign_and_degree(abs_deg)
        is_odd = (sign % 2 == 0)
        shashtiamsa = int(deg * 2)
        final_sign = (sign + shashtiamsa) % 12 if is_odd else (sign + (59 - shashtiamsa)) % 12
        chart[planet] = final_sign + 1
    # Ascendant
    sign, deg = get_sign_and_degree(asc_deg)
    is_odd = (sign % 2 == 0)
    shashtiamsa = int(deg * 2)
    final_sign = (sign + shashtiamsa) % 12 if is_odd else (sign + (59 - shashtiamsa)) % 12
    chart['Ascendant'] = final_sign + 1
    return chart

def get_d9_chart(planets_raw, asc_deg):
    chart = {}
    for planet, abs_deg in planets_raw.items():
        sign, deg = get_sign_and_degree(abs_deg)
        navamsa_index = int(deg * 3)
        if sign % 2 == 0:
            final_sign = (sign + navamsa_index) % 12
        else:
            final_sign = (sign + (8 - navamsa_index)) % 12
        chart[planet] = final_sign + 1
    # Ascendant
    sign, deg = get_sign_and_degree(asc_deg)
    navamsa_index = int(deg * 3)
    if sign % 2 == 0:
        final_sign = (sign + navamsa_index) % 12
    else:
        final_sign = (sign + (8 - navamsa_index)) % 12
    chart['Ascendant'] = final_sign + 1
    return chart

def get_d30_chart(planets_raw, asc_deg):
    chart = {}
    def trimsamsa_calc(sign, deg):
        if sign % 2 == 0:
            if deg <= 5:
                return 6  # Venus
            elif deg <= 10:
                return 10  # Jupiter
            elif deg <= 18:
                return 8  # Mercury
            elif deg <= 25:
                return 1  # Mars
            else:
                return 11  # Saturn
        else:
            if deg <= 5:
                return 11  # Saturn
            elif deg <= 12:
                return 1  # Mars
            elif deg <= 20:
                return 8  # Mercury
            elif deg <= 25:
                return 10  # Jupiter
            else:
                return 6  # Venus

    for planet, abs_deg in planets_raw.items():
        sign, deg = get_sign_and_degree(abs_deg)
        chart[planet] = trimsamsa_calc(sign, deg)
    # Ascendant
    sign, deg = get_sign_and_degree(asc_deg)
    chart['Ascendant'] = trimsamsa_calc(sign, deg)
    return chart

def get_d60_chart(planets_raw, asc_deg):
    chart = {}
    for planet, abs_deg in planets_raw.items():
        d60_sign = int(abs_deg * 2) % 12
        chart[planet] = d60_sign + 1
    chart['Ascendant'] = int(asc_deg * 2) % 12 + 1
    return chart
