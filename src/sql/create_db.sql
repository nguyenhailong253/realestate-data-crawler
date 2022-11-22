-- Create table
create table if not exists PropertyListings (
	id bigserial PRIMARY KEY,
	address text,
	price varchar(255),
	agency_property_listings_url text,
	agency_logo text,
	property_images text[],
	property_url varchar(100),
	property_id varchar(50),
	move_in_date varchar(20),
	listing_title text,
	listing_description text,
	num_bedrooms varchar(2),
	num_bathrooms varchar(2),
	num_garages varchar(2),
	property_features varchar(50)[],
	google_maps_location_url text,
	gps_coordinates varchar(255),
	suburb varchar(255),
	state_and_territory varchar(20),
	postcode varchar(10),
	agent_name varchar(255),
	off_market boolean not null,
	ad_details_included boolean not null,
	ad_removed_date timestamp,
	ad_posted_date timestamp,
	data_collection_date timestamp not null
)


-- Select number of distinct states
SELECT COUNT(DISTINCT state_and_territory) AS states FROM raw.propertylistings

-- Find duplicates
select max(id), property_id, property_url, ad_posted_date, count(*) 
			from raw.propertylistings 
			group by property_id, property_url, ad_posted_date having count(*) > 1

-- Delete duplicates
delete from raw.propertylistings
	where id in
	(
		select max(id)
			from raw.propertylistings 
			group by property_id, property_url having count(*) > 1

	)

-- Update a column
update raw.propertylistings set ad_posted_date = NOW() + INTERVAL '6 day' where id = '...'

-- Create index for a column
create index idx_property_id on raw.propertylistings(property_id)