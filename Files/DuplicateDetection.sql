SELECT
    "UniqueKey",
    COUNT(*) AS occurrences
FROM evaluation."EvaluationTable"
-- WHERE "IsEvaluated" = True
GROUP BY "UniqueKey"--, "AssignmentDate"
HAVING COUNT(*) > 1;