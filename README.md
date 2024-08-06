To run test for the sort_by_distance:
1. pip install -r requirements.txt (pytest-django)
2. run pytest


Steps on how to setup and use the application.
1. In the project folder directory, run command pip install -r requirements.txt
2. run command python manage.py makemigrations and python manage.py migrate
3. to create a superuser, run command python manage.py createsuperuser
4. You may access the admin page in Localhost-URL/admin ex. localhost:8000/admin. You can create Users, Ride, RideEvents
5. You can access the API Documentation or Swagger at this URL /swagger. ex. localhost:8000/swagger
6. To obtain token please find path /token and fill out necessary fields. 
7. To use the authorization of swagger please use the "Authorize" button and Type Bearer + access_token. ex: Bearer 830921hdjksadh20387193821dsjkla
8. To access the ride list please find path /rides , you can use the sorting by GPS Position by inputting lattitude and longitude.


Bonus SQL

Note(in ride events please type in the description. and use 'Status changed to pickup' for pickup and 'Status changed to dropoff'  for dropoff status.)

with connection.cursor() as cursor:

    cursor.execute(
        """
    WITH RideTimes AS (
        SELECT r.id_ride,
            r.id_driver_id,
            (SELECT created_at
                FROM base_rideevent
                WHERE id_ride = r.id_ride
                AND description = 'Status changed to pickup'
                ORDER BY created_at
                LIMIT 1) AS time_of_pickup,
            (SELECT created_at
                FROM base_rideevent
                WHERE id_ride = r.id_ride
                AND description = 'Status changed to dropoff'
                ORDER BY created_at
                LIMIT 1) AS time_of_dropoff
        FROM base_ride r
    ),
    RideDurations AS (
        SELECT id_ride,
            id_driver_id,
            time_of_pickup,
            time_of_dropoff,
            (julianday(time_of_dropoff) - julianday(time_of_pickup)) * 86400 AS duration_seconds
        FROM RideTimes
        WHERE time_of_pickup IS NOT NULL AND time_of_dropoff IS NOT NULL
    )
    SELECT  strftime('%Y-%m', rd.time_of_pickup) AS month,
    u.first_name || ' ' || u.last_name AS driver_name,
    COUNT(rd.id_ride) AS ride_count,
    rd.duration_seconds AS duration
    FROM RideDurations rd
    JOIN base_user u ON rd.id_driver_id = u.id_user
    WHERE rd.duration_seconds > 3600
    GROUP BY driver_name, month
    ORDER BY driver_name, month;
    """
    )
    rows = cursor.fetchall()
    for row in rows:
        print(f"Month: {row[0]}, Driver Name: {row[1]}, Ride Trip > 1 Hour Count: {row[2]}")
