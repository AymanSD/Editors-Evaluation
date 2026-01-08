SELECT "EditorName", SUM(CaseCount) AS CaseCount FROM
(
SELECT --* 
"EditorName",
-- "AssignedSupervisor", 
COUNT(*) AS CaseCount
FROM 
evaluation."CaseAssignment"
WHERE 
"EditorName" IN (SELECT "EditorName" FROM evaluation."EditorsList" WHERE "GroupID" IN ('Editor Morning Shift', 'Editor Night Shift'))
AND
"IsEvaluated" = FALSE
AND 
"IsRetired" = FALSE
GROUP BY "EditorName" --"AssignedSupervisor" 
UNION (SELECT "EditorName", COUNT(*) AS CaseCount FROM evaluation."EvaluationTable"
WHERE "EditorName" IN (SELECT "EditorName" FROM evaluation."EditorsList" WHERE "GroupID" IN ('Editor Morning Shift', 'Editor Night Shift'))
GROUP BY "EditorName")
-- ORDER BY "EditorName"
) t
GROUP BY "EditorName"

