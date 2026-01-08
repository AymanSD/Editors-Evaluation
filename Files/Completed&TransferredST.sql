SELECT
    [Transferred to Geospatial],
    SUM(CurrentCount)   AS CurrentCount,
    SUM(CompletedCount) AS CompletedCount
FROM (
    SELECT
        [Transferred to Geospatial],
        COUNT(*) AS CurrentCount,
        0 AS CompletedCount
    FROM grsdbrd.[MG_Current]
    WHERE [Transferred to Geospatial] BETWEEN '2025-12-28' AND  '2025-12-29'
    GROUP BY [Transferred to Geospatial]

    UNION ALL

    SELECT
        [Transferred to Geospatial],
        0 AS CurrentCount,
        COUNT(*) AS CompletedCount
    FROM grsdbrd.[MG_Data]
    WHERE [Transferred to Geospatial] BETWEEN '2025-12-28' AND  '2025-12-29'
    GROUP BY [Transferred to Geospatial]
) t
GROUP BY [Transferred to Geospatial]
ORDER BY [Transferred to Geospatial];

-- UNION ALL
SELECT
    [GEO Completion],
    SUM(CompletedCases)   AS CompletedCases
    FROM (
        SELECT [GEO Completion], COUNT(*) AS CompletedCases FROM GRSDBRD.MG_Data
        WHERE [GEO Completion] BETWEEN '2025-12-28' AND '2025-12-29'
        GROUP BY [GEO Completion]
    ) f
    GROUP BY [GEO Completion]