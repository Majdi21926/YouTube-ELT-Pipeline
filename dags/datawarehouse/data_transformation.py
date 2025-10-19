from datetime import timedelta, datetime

# parse duration, the dration is on ISO 8601 format, 
# The function will give a timedelta object, duration
def parse_duration(duration):

    duration = duration.replace('P', '').replace("T", "") 

    components = ['D', 'H', 'M', 'S']
    values = {'D': 0, 'H': 0, 'M': 0, 'S': 0}

    for component in components:
        if component in duration:
            value, duration = duration.split(component)
            values[component] = int(value)

    total_duration = timedelta(
        days=values['D'],
        hours=values['H'],
        minutes=values['M'],
        seconds=values['S']
    )
    return total_duration

# transform_data function to transform data from staging to core
# It will parse the duration and add video type
def transform_data(row):

    duration_td = parse_duration(row['Duration']) # apply transformation on duration
    row['Duration'] = (datetime.min + duration_td).time() # convert timedelta to time object

    row['Video_Type'] = 'Short' if duration_td.total_seconds() <= 60 else 'Normal' # add video type based on duration
    return row