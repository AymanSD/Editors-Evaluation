WITH limited_cases AS (
    SELECT
        *,
        ROW_NUMBER() OVER (
            PARTITION BY "EditorName"
            ORDER BY "CompletionDate" DESC  -- choose the order you want
        ) AS rn
    FROM evaluation."EvaluationTable"
    WHERE "EditorName" IN (
        SELECT "CasePortalName"
        FROM evaluation."EditorsList"
        WHERE "GroupID" IN ('Pod-Al-Shuhada-1', 'Pod-Al-Shuhada-2', 'Urgent Team')
		-- WHERE "GroupID" IN ('Editor Morning Shift', 'Editor Night Shift')
    )
)
SELECT
    "EditorName",
    COUNT(*) AS CasesCount,
    COUNT(*) FILTER (WHERE "GeoAction" = 'رفض') AS RejectCount,
    COUNT(*) FILTER (WHERE "GeoAction" <> 'رفض') AS EditCount,
    AVG("TechnicalAccuracy") AS "Avg. Technical Accuracy",
    AVG("ProceduralAccuracy") AS "Avg. Procedural Accuracy"
FROM limited_cases
WHERE rn <= 25
GROUP BY "EditorName"
ORDER BY "EditorName";
