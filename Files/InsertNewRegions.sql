-- SELECT * FROM evaluation."Regions"
INSERT INTO evaluation."Regions" ("CityName", "Region")
-- VALUES ('الشملي', 'Hael');
SELECT 'سميراء', 'Hael' 
WHERE NOT EXISTS (
SELECT 1 FROM evaluation."Regions"
WHERE "CityName" = 'سميراء')