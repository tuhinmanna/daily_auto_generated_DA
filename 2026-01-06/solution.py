```sql
WITH StageOutcomes AS (
    SELECT
        stage_name,
        SUM(CASE WHEN status = 'Rejected' THEN 1 ELSE 0 END) AS rejected_at_stage_count,
        COUNT(DISTINCT application_id) AS total_applications_completed_stage
    FROM
        application_stages
    WHERE
        status IN ('Passed', 'Rejected', 'Withdrew', 'Hired') -- Filter for applications that completed the stage with a final outcome
    GROUP BY
        stage_name
)
SELECT
    stage_name,
    rejected_at_stage_count,
    total_applications_completed_stage,
    (CAST(rejected_at_stage_count AS DECIMAL) * 100.0 / total_applications_completed_stage) AS rejection_percentage
FROM
    StageOutcomes
WHERE
    total_applications_completed_stage > 0 -- Exclude stages with no completed applications to avoid division by zero
ORDER BY
    rejection_percentage DESC
LIMIT 3;
```