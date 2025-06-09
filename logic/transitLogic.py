

def prepare_divisional_chart(planet_data, asc_zodiac_number):
    """Returns house-wise placements with planets and zodiac signs: {1: {"planets": [...], "zodiac": ...}, ...}"""
    chart = {i: {"planets": [], "zodiac": None} for i in range(1, 13)}

    # Assign zodiac number to each house based on ascendant
    for i in range(12):
        house = i + 1
        zodiac_number = (asc_zodiac_number + i - 1) % 12 + 1
        chart[house]["zodiac"] = zodiac_number

    # Place planets in correct house
    for planet, pdata in planet_data.items():
        zodiac_num = zodiac_to_number(pdata['zodiac'])
        degree = pdata['degree']
        house = (zodiac_num - asc_zodiac_number + 12) % 12 + 1
        chart[house]["planets"].append(f"{planet}^{degree:.5f} ({zodiac_num})")

    # Add "Ascendant" label to 1st house
    chart[1]["planets"].insert(0, "Ascendant")

    return chart


def zodiac_to_number(zodiac):
    """Map zodiac sign name to number (1 = Aries, ..., 12 = Pisces)"""
    zodiac_signs = [
        'Aries', 'Taurus', 'Gemini', 'Cancer', 'Leo', 'Virgo',
        'Libra', 'Scorpio', 'Sagittarius', 'Capricorn', 'Aquarius', 'Pisces'
    ]
    return zodiac_signs.index(zodiac) + 1