from datetime import timedelta, datetime
from flask import session

DASHA_SEQUENCE = [
    ('Ketu', 7), ('Venus', 20), ('Sun', 6), ('Moon', 10),
    ('Mars', 7), ('Rahu', 18), ('Jupiter', 16), ('Saturn', 19), ('Mercury', 17)
]

def get_dasha_start(moon_long):
    nakshatra_index = int(moon_long // (13 + 1/3))
    lord = DASHA_SEQUENCE[nakshatra_index % 9][0]

    dasha_years = dict(DASHA_SEQUENCE)[lord]
    degrees_in_nakshatra = moon_long % (13 + 1/3)
    proportion_passed = degrees_in_nakshatra / (13 + 1/3)
    balance_years = dasha_years * (1 - proportion_passed)

    return lord, balance_years




def calculate_dasha_levels(start_datetime, moon_long):
    # Step 1: Get initial Mahadasha and balance
    maha_lord, balance_years = get_dasha_start(moon_long)
    dasha_list = []

    # Step 2: Compute actual Mahadasha start from birth
    maha_index = [d[0] for d in DASHA_SEQUENCE].index(maha_lord)
    maha_start_actual = start_datetime - timedelta(days=balance_years * 365.25)
    current_date = maha_start_actual

    # Step 3: Loop through 9 Mahadashas
    for i in range(9):
        maha_lord, maha_years = DASHA_SEQUENCE[(maha_index + i) % 9]
        maha_start = current_date
        maha_end = maha_start + timedelta(days=maha_years * 365.25)

        mahadasha_data = {
            'mahadasha': maha_lord,
            'start': maha_start,
            'end': maha_end,
            'antardashas': []
        }

        # Step 4: Calculate Antardasha inside Mahadasha
        antar_start = maha_start
        for antar_lord, antar_years in DASHA_SEQUENCE:
            antar_duration = (maha_end - maha_start).total_seconds() * (antar_years / 120)
            antar_end = antar_start + timedelta(seconds=antar_duration)

            antardasha_data = {
                'antardasha': antar_lord,
                'start': antar_start,
                'end': antar_end,
                'pratyantardashas': []
            }

            # Step 5: Pratyantar inside Antardasha
            praty_start = antar_start
            for praty_lord, praty_years in DASHA_SEQUENCE:
                praty_duration = (antar_end - antar_start).total_seconds() * (praty_years / 120)
                praty_end = praty_start + timedelta(seconds=praty_duration)

                praty_data = {
                    'pratyantardasha': praty_lord,
                    'start': praty_start,
                    'end': praty_end,
                    'sookshma': []
                }

                # Step 6: Sookshma inside Pratyantar
                sook_start = praty_start
                for sook_lord, sook_years in DASHA_SEQUENCE:
                    sook_duration = (praty_end - praty_start).total_seconds() * (sook_years / 120)
                    sook_end = sook_start + timedelta(seconds=sook_duration)

                    praty_data['sookshma'].append({
                        'sookshmadasha': sook_lord,
                        'start': sook_start,
                        'end': sook_end
                    })
                    sook_start = sook_end

                antardasha_data['pratyantardashas'].append(praty_data)
                praty_start = praty_end

            mahadasha_data['antardashas'].append(antardasha_data)
            antar_start = antar_end

        dasha_list.append(mahadasha_data)
        current_date = maha_end

    return dasha_list



def get_full_dasha_from_session():
    moon_long = session.get('moon_degree')
    birth_date = session.get('birth_datetime')
    time_str = session.get('timestr')

    if not moon_long or not birth_date or not time_str:
        return []

    start_datetime = datetime.strptime(f"{birth_date} {time_str}", "%d-%m-%Y %H:%M")
    return calculate_dasha_levels(start_datetime, moon_long)


