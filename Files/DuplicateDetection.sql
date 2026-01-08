SELECT
    "UniqueKey",
    COUNT(*) AS occurrences
FROM evaluation."CaseAssignment"
-- WHERE "IsEvaluated" = True
GROUP BY "UniqueKey"--, "AssignmentDate"
HAVING COUNT(*) > 1;