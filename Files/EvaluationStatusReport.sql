
-- Assignment
SELECT "AssignmentDate", COUNT(*) AS "Assigned",
COUNT(*) FILTER (WHERE "GeoAction" = 'رفض') AS "Assigned Reject",
COUNT(*) FILTER (WHERE "GeoAction" = 'رفض') AS "Assigned Edit",
COUNT(*) FILTER (WHERE "IsEvaluated" = TRUE) AS "Evaluated",
COUNT(*) FILTER (WHERE "IsEvaluated" = False) AS "In Progress"
FROM evaluation."CaseAssignment"
WHERE "AssignmentDate" >= '2026-01-01'
AND "IsRetired" = FALSE
GROUP BY "AssignmentDate"
ORDER BY "AssignmentDate"


--Evaluation
SELECT "EvaluationDate"::date, COUNT(*) AS "Evaluated",
COUNT(*) FILTER (WHERE "GeoAction" = 'رفض') AS "Evaluated Reject",
COUNT(*) FILTER (WHERE "GeoAction" = 'رفض') AS "Evaluated Edit"
FROM evaluation."EvaluationTable"
WHERE "EvaluationDate"::date >= '2026-01-01'
GROUP BY "EvaluationDate"::date
ORDER BY "EvaluationDate"