SELECT DISTINCT("Case Number") FROM public."ApprovedCases"
WHERE "GEO S Completion" IS NOT NULL OR "GEO S Completion" IS NOT NULL
-- AND "Latest Action Date" BETWEEN '2025-01-01' AND '2025-12-31'
-- SELECT * FROM public."ApprovedCases"
-- WHERE "Geo Supervisor Recommendation" IS NOT NULL
-- LIMIT 10

SELECT COUNT(DISTINCT("Case Number")) FROM public."ApprovedCases"
WHERE 
("Geo Supervisor Recommendation" IS NOT NULL
 OR "GEO S Completion" IS NOT NULL)
 AND "Latest Action Date" BETWEEN '2025-01-01' AND '2025-12-31'
 -- AND 
SELECT COUNT(DISTINCT("Case Number")) FROM public."ApprovedCases"
WHERE "Latest Action Date" BETWEEN '2024-01-01' AND '2024-12-31'
AND ("Geo Supervisor Recommendation" IS NOT NULL
 OR "GEO S Completion" IS NOT NULL)

SELECT COUNT(DISTINCT("Case Number")) FROM public."ApprovedCases"
WHERE "Latest Action Date" BETWEEN '2026-01-01' AND '2026-12-31'
AND ("Geo Supervisor Recommendation" IS NOT NULL
OR "GEO S Completion" IS NOT NULL)