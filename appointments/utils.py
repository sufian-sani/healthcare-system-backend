from datetime import datetime, timedelta

def generate_30_min_slots(start_time, end_time):
    slots = []
    current = datetime.combine(datetime.today(), start_time)
    end = datetime.combine(datetime.today(), end_time)

    while current < end:
        slots.append(current.time())
        current += timedelta(minutes=30)
    return slots
