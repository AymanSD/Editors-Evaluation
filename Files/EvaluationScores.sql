-- SELECT * FROM evaluation."EvaluationTable"
SELECT
    "EditorName",
    AVG("TechnicalAccuracy")*100 AS avg_technical_accuracy,
    AVG("ProceduralAccuracy")*100 AS avg_procedural_accuracy
FROM
    evaluation."EvaluationTable"
WHERE "EvaluationDate"::date BETWEEN '2025-12-10' AND '2025-12-14'
GROUP BY
    "EditorName"
ORDER BY "EditorName"