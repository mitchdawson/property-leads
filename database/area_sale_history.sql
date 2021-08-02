SELECT id, rm_property_id, rm_postcode, rm_sold_nearby_url, rm_real_address_attempted
FROM properties
WHERE rm_sale_history_attempted = true
AND rm_sold_nearby_url IS NOT NULL
AND rm_real_address IS NULL
AND rm_real_address_attempted = true
AND id IN (
	SELECT property_id
	FROM sale_history
)
ORDER BY created ASC;

-- update properties
-- set rm_real_address_attempted = false
-- WHERE rm_sale_history_attempted = true
-- AND rm_sold_nearby_url IS NOT NULL
-- AND rm_real_address IS NULL
-- AND rm_real_address_attempted = true
-- AND id IN (
-- 	SELECT property_id
-- 	FROM sale_history
-- );