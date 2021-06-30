-- SELECT
-- id,
-- "locationIdentifier",
-- "maxPrice",
-- "minPrice",
-- "radius",
-- "propertyTypes",
-- "primaryDisplayPropertyType",
-- "includeSSTC",
-- "dontShow",
-- accessed
-- FROM urls
-- WHERE accessed::timestamp < (now() - INTERVAL '48 hours')
-- ORDER BY accessed asc;
-- update urls set accessed = '2021-06-17 20:51:52' where description like 'Chelmsford%';
-- select * from urls where description like 'Chelmsford%' order by accessed asc;
-- update urls set description = 'Chelmsford, Essex' where description like 'Chelmsford%';
-- update properties 
-- set rm_postcode = NULL, rm_sold_nearby_url = NULL 
-- where rm_real_address IS NULL;
-- id = 'c896d97c-97ce-4617-a577-71fc3d991a08';
select * from properties WHERE rm_epc_cert_url IS NOT NULL;

-- delete from sale_history where property_id in (select id from properties where rm_postcode IS NULL)
-- SELECT
-- id, rm_property_url, 
-- rm_postcode, rm_sold_nearby_url
-- FROM properties
-- WHERE rm_postcode IS NULL
-- ORDER BY created ASC LIMIT 200;

-- Properties with no sale history
-- SELECT
-- rm_display_address,
-- rm_real_address,
-- rm_property_url,
-- rm_postcode,
-- rm_sold_nearby_url,
-- rm_real_address_attempted,
-- rm_sale_history_attempted,
-- rm_display_status,
-- rm_listing_price,
-- rm_first_visible_date,
-- rm_sold_stc_timestamp,
-- created
-- FROM properties
-- WHERE rm_sale_history_attempted = false
-- AND rm_postcode IS NOT NULL
-- AND id NOT IN (SELECT property_id FROM sale_history)
-- ORDER BY created ASC;


-- SELECT *  from sale_history WHERE property_id IN (SELECT id from properties);



-- AND id NOT IN (
-- 	SELECT property_id
-- 	FROM sale_history
-- )

-- select count(*) from properties where rm_real_address IS NOT NULL;

-- SELECT id, rm_property_id, rm_postcode, rm_sold_nearby_url
-- FROM properties
-- WHERE rm_sale_history_attempted = true
-- AND rm_sold_nearby_url IS NOT NULL
-- AND rm_real_address IS NULL
-- AND rm_real_address_attempted = false
-- AND id IN (
-- 	SELECT property_id
-- 	FROM sale_history
-- );

-- select
-- rm_display_address,
-- rm_real_address,
-- rm_property_url,
-- rm_postcode,
-- rm_sold_nearby_url,
-- rm_real_address_attempted,
-- rm_sale_history_attempted,
-- rm_display_status,
-- rm_listing_price,
-- rm_first_visible_date,
-- rm_sold_stc_timestamp,
-- created
-- from properties 
-- where rm_sale_history_attempted = false
-- ORDER BY created asc;

-- update properties set rm_real_address_attempted = true where rm_real_address IS NOT NULL;
-- select * from sale_history ORDER BY created desc;
-- select * from properties;
-- delete from sale_history;
-- update properties set rm_sale_history_attempted = false where rm_sale_history_attempted = true;
-- select id, accessed from urls
-- WHERE accessed::timestamp < (now() - INTERVAL '48 hours') order by accessed desc;

-- delete from properties where rm_property_url LIKE '%107534963%';
-- select id, accessed from urls order by accessed desc;
-- update urls set accessed = '2021-05-25 10:52:26.277063' where id = '32d7efe3-2d50-4e34-942b-f3a7fefb1e81';
-- select id, accessed from urls order by accessed asc;
-- select id, accessed from urls order by accessed asc;
-- select * from urls where id = '32d7efe3-2d50-4e34-942b-f3a7fefb1e81';
select
rm_postcode,
rm_real_address,
rm_display_status,
rm_listing_price,
rm_first_visible_date,
rm_sold_stc_timestamp,
created
from properties where rm_real_address IS NOT NULL ORDER BY created desc;

-- delete from properties WHERE rm_commercial = 'true';
-- select * from urls;rm_commercial
-- 
-- update urls set description = 'Southend, Essex', accessed = '2021-05-25 10:52:26.277063' where "locationIdentifier" = 'REGION^1232';
-- select description, accessed from urls where "locationIdentifier" = 'REGION^1232';
-- select count(*) from properties where rm_sold_stc_timestamp is not NULL;
-- SELECT
-- id,
-- accessed,
-- "locationIdentifier",
-- "maxPrice",
-- "minPrice",
-- "radius",
-- "propertyTypes",
-- "primaryDisplayPropertyType",
-- "includeSSTC",
-- "dontShow"
-- FROM urls
-- WHERE accessed::timestamp < (now() - INTERVAL '48 hours')
-- delete from properties where rm_property_id = '85866424';
-- select * from properties where rm_property_url like '/properties/86615171';
-- select * from properties where rm_property_id = '99662612';
-- select from sale_history where property_id = (select id from properties WHERE rm_property_id = '99662612');
-- delete from properties where rm_property_id = '95658227'

-- select * from properties where id = '166ad4c6-91ac-4344-8bbd-b1131b6799af';
-- update properties set rm_epc_cert_address = NULL, rm_epc_cert_address_attempted = false where id = '166ad4c6-91ac-4344-8bbd-b1131b6799af';
