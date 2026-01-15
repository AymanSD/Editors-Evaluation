SELECT COUNT(DISTINCT("Case Number"))
FROM "SR_Data"
WHERE "Case Number" NOT IN (SELECT "Case Number" FROM public."SR_Current")
-- WHERE "Transferred to Geospatial" BETWEEN '2025-11-01' AND '2025-11-31'
UNION
SELECT COUNT(DISTINCT("Case Number"))
FROM "MG_Data"
WHERE "Case Number" NOT IN (SELECT "Case Number" FROM public."MG_Current")
-- WHERE "Transferred to Geospatial" BETWEEN '2025-11-01' AND '2025-11-31'
UNION
SELECT COUNT(DISTINCT("Case Number"))
FROM "CR_Data"
WHERE "Case Number" NOT IN (SELECT "Case Number" FROM public."CR_Current")
-- WHERE "Transferred to Geospatial" BETWEEN '2025-11-01' AND '2025-11-31'
