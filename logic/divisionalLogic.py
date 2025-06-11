ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]

def get_sign_and_degree(abs_deg):
    sign = int(abs_deg // 30)  # 0–11
    deg = abs_deg % 30
    return sign, deg

# def get_absolute_degree(sign_index, degree_in_sign):
#     return sign_index * 30 + degree_in_sign

def get_absolute_degree(sign_index, degree_in_sign):
    return float(sign_index) * 30 + float(degree_in_sign)

def get_sign_and_degree(absolute_deg):
    sign = int(absolute_deg // 30)
    degree_in_sign = absolute_deg % 30
    return sign, degree_in_sign



def rotate_chart(mapping, asc_sign_index):
    # Create rotated structure
    rotated = {i: {'planets': [], 'zodiac': ''} for i in range(1, 13)}

    # Determine original sign index of each house
    sign_to_house = {((asc_sign_index + i) % 12) + 1: i + 1 for i in range(12)}

    # Step 1: Move all planets to correct rotated houses
    for body, house in mapping.items():
        if body == "Ascendant":
            continue
        shift = (house - mapping["Ascendant"]) % 12
        new_house = shift + 1
        rotated[new_house]['planets'].append(body)

    # Step 2: Label rotated zodiac signs
    for i in range(1, 13):
        zodiac_index = (asc_sign_index + i - 1) % 12
        rotated[i]['zodiac'] = ZODIAC_SIGNS[zodiac_index] + f" ({zodiac_index + 1})"

    return rotated





def get_d1_chart(planets_raw, asc_deg):
    asc_sign_index = int(asc_deg // 30)  # 0 for Aries, 1 for Taurus, ..., 11 for Pisces
    chart = {}
    for planet, abs_deg in planets_raw.items():
        planet_sign_index = int(abs_deg // 30)
        house = ((planet_sign_index - asc_sign_index) % 12) + 1
        chart[planet] = house
    chart['Ascendant'] = 1  # Always 1st house
    return rotate_chart(chart, asc_sign_index)

def generic_chart(planets_raw, asc_deg, transform_fn):
    chart = {}
    for planet, abs_deg in planets_raw.items():
        chart[planet] = transform_fn(abs_deg)
    chart['Ascendant'] = transform_fn(asc_deg)
    asc_sign_index = int(asc_deg // 30)
    return rotate_chart(chart, asc_sign_index)



def get_d3_chart_from_d1(d1_planets_raw, d1_asc_deg):
    ZODIAC_SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    def get_sign_and_degree(abs_deg):
        sign = int(abs_deg // 30)
        degree_in_sign = abs_deg % 30
        return sign, degree_in_sign

    # Step 1: Drekkana transformation (used for both ascendant and planets now)
    def drekkana_transform(abs_deg):
        sign, deg = get_sign_and_degree(abs_deg)
        drekkana = int(deg // 10)
        if drekkana == 0:
            return sign  # 1st drekkana — same sign
        elif drekkana == 1:
            return (sign + 4) % 12  # 5th from current
        else:
            return (sign + 8) % 12  # 9th from current

    # ✅ CORRECTED: Apply D3 logic to Ascendant instead of Navamsa
    asc_sign_index = drekkana_transform(d1_asc_deg)

    # Step 2: Build chart using D3 rules
    chart = {}
    for planet, abs_deg in d1_planets_raw.items():
        if planet != 'Ascendant':
            transformed_sign = drekkana_transform(abs_deg)
            house = ((transformed_sign - asc_sign_index) % 12) + 1
            chart[planet] = house

    chart['Ascendant'] = 1  # Always place Ascendant in 1st house

    # Step 3: Final formatting and zodiac labels
    rotated = {i: {'planets': [], 'zodiac': ''} for i in range(1, 13)}
    for body, house in chart.items():
        rotated[house]['planets'].append(body)

    for i in range(1, 13):
        zodiac_index = (asc_sign_index + i - 1) % 12
        rotated[i]['zodiac'] = ZODIAC_SIGNS[zodiac_index] + f" ({zodiac_index + 1})"

    return rotated





def get_d6_chart(planets_raw, asc_deg):
    def transform(abs_deg):
        sign, deg = get_sign_and_degree(abs_deg)
        is_odd = (sign % 2 == 0)
        shashtiamsa = int(deg * 2)
        return ((sign + shashtiamsa) if is_odd else (sign + (59 - shashtiamsa))) % 12 + 1
    return generic_chart(planets_raw, asc_deg, transform)




def get_d9_chart(d1_planets_raw, d1_asc_deg):
    import math

    ZODIAC_SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    def get_sign_and_degree(abs_deg):
        sign = int(abs_deg // 30)
        degree_in_sign = abs_deg % 30
        return sign, degree_in_sign

    # Determine the start point for Navamsa based on D1 sign
    def get_navamsa_start_sign(d1_sign_index):
        if d1_sign_index in [0, 4, 8]:  # Aries, Leo, Sagittarius -> Navamsa starts at Aries
            return 0  # Aries
        elif d1_sign_index in [1, 5, 9]:  # Taurus, Virgo, Capricorn -> Navamsa starts at Capricorn
            return 9  # Capricorn
        elif d1_sign_index in [2, 6, 10]:  # Gemini, Libra, Aquarius -> Navamsa starts at Libra
            return 6  # Libra
        else:  # Cancer, Scorpio, Pisces -> Navamsa starts at Cancer
            return 3  # Cancer

    # Calculate Navamsa for Ascendant
    def navamsa_transform(abs_deg):
        sign, deg = get_sign_and_degree(abs_deg)
        navamsa_index = math.ceil((deg * 9) / 30)  # Calculates the Navamsa number (1–9)
        navamsa_start_sign = get_navamsa_start_sign(sign)  # Get the start point based on D1 sign
        
        # Calculate the new sign
        new_sign = (navamsa_start_sign + navamsa_index - 1) % 12
        return new_sign  # Return 0–11 index for the sign

    # Transform Ascendant into Navamsa sign
    asc_sign_index = navamsa_transform(d1_asc_deg)

    # Build chart for D9 (Navamsa)
    chart = {}
    for planet, abs_deg in d1_planets_raw.items():
        if planet != 'Ascendant':
            transformed_sign = navamsa_transform(abs_deg)  # Get Navamsa sign for the planet
            house = ((transformed_sign - asc_sign_index) % 12) + 1  # Calculate the house based on ascendant
            chart[planet] = house

    chart['Ascendant'] = 1  # Always place Ascendant in 1st house

    # Final formatting for D9 chart with zodiac
    rotated = {i: {'planets': [], 'zodiac': ''} for i in range(1, 13)}
    for body, house in chart.items():
        rotated[house]['planets'].append(body)

    for i in range(1, 13):
        zodiac_index = (asc_sign_index + i - 1) % 12
        rotated[i]['zodiac'] = ZODIAC_SIGNS[zodiac_index] + f" ({zodiac_index + 1})"

    return rotated






def get_d30_chart(d1_planets_raw, d1_asc_deg):
    import math

    ZODIAC_SIGNS = [
        "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
        "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
    ]

    def get_sign_and_degree(abs_deg):
        sign = int(abs_deg // 30)
        degree_in_sign = abs_deg % 30
        return sign, degree_in_sign

    # Define the Trimsamsa division for each sign (odd and even signs)
    def trimsamsa_transform(abs_deg):
        sign, deg = get_sign_and_degree(abs_deg)

        # For odd signs (Aries, Gemini, Leo, Sagittarius, Libra, Aquarius)
        if sign in [0, 2, 4, 6, 8, 10]:  # Odd signs
            if deg <= 5:  # First 5 degrees of the sign
                new_sign = 0  # Aries
            elif deg <= 8:  # Next 3 degrees of the sign
                new_sign = 1  # Aquarius
            elif deg <= 16:  # Next 8 degrees
                new_sign = 2  # Sagittarius
            elif deg <= 23:  # Next 7 degrees
                new_sign = 3  # Gemini
            else:  # Next 5 degrees
                new_sign = 4  # Libra

        # For even signs (Taurus, Cancer, Virgo, Scorpio, Capricorn, Pisces)
        else:  # Even signs
            if deg <= 5:
                new_sign = 5  # Taurus
            elif deg <= 7:
                new_sign = 6  # Virgo
            elif deg <= 15:
                new_sign = 7  # Pisces
            elif deg <= 22:
                new_sign = 8  # Capricorn
            else:
                new_sign = 9  # Scorpio

        return new_sign  # This returns the 0–11 index of the sign in D30

    # Calculate D30 positions for the Ascendant and planets
    chart = {}
    asc_sign_index = trimsamsa_transform(d1_asc_deg)  # Ascendant D30 position

    # Loop through planets to calculate D30 positions
    for planet, abs_deg in d1_planets_raw.items():
        if planet != 'Ascendant':
            transformed_sign = trimsamsa_transform(abs_deg)  # Get D30 position for the planet
            house = ((transformed_sign - asc_sign_index) % 12) + 1  # Calculate the house based on Ascendant
            chart[planet] = house

    chart['Ascendant'] = 1  # Always place Ascendant in the 1st house of D30

    # Final formatting for D30 chart with zodiac names
    rotated = {i: {'planets': [], 'zodiac': ''} for i in range(1, 13)}
    for body, house in chart.items():
        rotated[house]['planets'].append(body)

    for i in range(1, 13):
        zodiac_index = (asc_sign_index + i - 1) % 12
        rotated[i]['zodiac'] = ZODIAC_SIGNS[zodiac_index] + f" ({zodiac_index + 1})"

    return rotated




def get_d60_chart(planets_raw, asc_deg):
    def transform(abs_deg):
        return int(abs_deg * 2) % 12 + 1
    return generic_chart(planets_raw, asc_deg, transform)
