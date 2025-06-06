# divisional.py

def get_d3_chart(planets_d1):
    d3_chart = {}
    for planet, degree in planets_d1.items():
        d3_sign = (int(degree // 10) % 12) + 1  # Parashara D3 rule
        d3_chart[planet] = d3_sign
    return d3_chart

def get_d9_chart(planets_d1):
    d9_chart = {}
    for planet, degree in planets_d1.items():
        d9_sign = ((int(degree * 9 // 30)) % 12) + 1  # Parashara D9 logic
        d9_chart[planet] = d9_sign
    return d9_chart



def get_d6_chart(planets_d1):
    pass

def get_d30_chart(planets_d1):
    pass

def get_d60_chart(planet_d1):
    pass

