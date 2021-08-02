-- SELECT id, rm_property_id, rm_postcode, rm_sold_nearby_url
-- FROM properties
-- WHERE rm_sale_history_attempted = true
-- AND rm_sold_nearby_url IS NOT NULL
-- AND rm_real_address IS NULL
-- AND rm_real_address_attempted = false
-- AND id IN (
--     SELECT property_id
--     FROM sale_history
-- )
-- LIMIT 200;

select count(*) from sale_history;