SELECT "EvaluatedBy", COUNT(*) AS "CasesCount", COUNT(DISTINCT("EditorName")) AS "EditorCount" FROM evaluation."EvaluationTable"
WHERE "EvaluationDate"::date = CURRENT_DATE-1
AND "GeoAction" <> 'رفض'
GROUP BY "EvaluatedBy"