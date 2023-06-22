SELECT 
tpep_pickup_datetime,
tpep_dropoff_datetime,
total_amount,
CONCAT(PUL."Borough", '/',PUL."Zone") as "Pickup_Location",
CONCAT(DOL."Borough", '/', DOL."Zone") as "Dropoff_Location"
FROM 
	public.yellow_taxi_trips as trips,
	public.zones as PUL,
	public.zones as DOL
where 
trips."PULocationID" = PUL."LocationID"
AND
trips."DOLocationID" = DOL."LocationID"
limit 10 ;
