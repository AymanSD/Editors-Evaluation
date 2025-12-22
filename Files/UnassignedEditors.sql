SELECT "CasePortalName" FROM evaluation."EditorsList"
WHERE "GroupID" IN ('Editor Morning Shift', 'Editor Night Shift', 
		'Pod-Al-Shuhada-1', 'Pod-Al-Shuhada-2', 'Urgent Team')
AND "CasePortalName" NOT IN (
	SELECT "EditorName" FROM evaluation."CaseAssignment"
	WHERE "AssignmentDate" = CURRENT_DATE
)
-- SELECT "AssignedSupervisor", COUNT(*) FROM evaluation."CaseAssignment"

-- WHERE "AssignmentDate" = CURRENT_DATE
-- -- ORDER BY "AssignmentID" ASC 
-- GROUP BY "AssignedSupervisor"