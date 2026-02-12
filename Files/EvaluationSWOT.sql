SELECT "EditorName",
	AVG("ProcedureScore") AS "Procedure Avg.", 
	AVG("RecommendationScore") AS "Recommendation Avg.", 
	AVG("TopologyScore") AS "Topology Avg.", 
	AVG("CompletenessScore") AS "Completeness Avg.", 
	AVG("BlockAlignmentScore") AS "BlockAlignment Avg.", COUNT(*) AS "EvaluatedCases",
  COUNT(*) FILTER (WHERE "GeoAction" = 'رفض')  AS "RejectCount",
  COUNT(*) FILTER (WHERE "GeoAction" <> 'رفض') AS "EditCount"
FROM evaluation."EvaluationTable"
WHERE "EvaluationDate"::date >= '2026-01-01'
GROUP BY "EditorName"

SELECT "EditorName", 
	COUNT(*) AS "Assigned Cases",
	COUNT(*) FILTER (WHERE "GeoAction" = 'رفض')  AS "RejectCount",
	COUNT(*) FILTER (WHERE "GeoAction" <> 'رفض') AS "EditCount",
	COUNT(*) FILTER (WHERE "IsEvaluated" = FALSE) AS "In Progress",
	COUNT(*) FILTER	 (WHERE "IsEvaluated" = TRUE) AS "Evaluated"
FROM evaluation."CaseAssignment"
WHERE "AssignmentDate" >= '2026-01-01'
AND "IsRetired" = FALSE
GROUP BY "EditorName"
