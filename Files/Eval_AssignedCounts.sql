SELECT 
    -- "EditorName",
    COUNT(*) AS "AssignedCount",
    COUNT(*) FILTER (WHERE "IsEvaluated" = TRUE) AS "EvaluatedCount",
	COUNT(*) FILTER (WHERE "IsEvaluated" = FALSE) AS "InProgressCount"
FROM evaluation."CaseAssignment"
WHERE "AssignmentDate" BETWEEN '2026-01-01' AND '2026-01-24'
AND "IsRetired" = True
-- GROUP BY "EditorName"
-- ORDER BY "EditorName";


SELECT
    "EvaluatedBy",
    COUNT(*) AS "AssignedCount"
 --    COUNT(*) FILTER (WHERE "IsEvaluated" = TRUE) AS "EvaluatedCount",
	-- COUNT(*) FILTER (WHERE "IsEvaluated" = FALSE) AS "InProgressCount"
FROM evaluation."EvaluationTable"
WHERE "EvaluationDate"::date BETWEEN '2026-01-01' AND '2026-01-24'
-- AND "IsRetired" = FALSE
GROUP BY "EvaluatedBy"
ORDER BY "EvaluatedBy";
