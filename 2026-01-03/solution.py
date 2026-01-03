WITH funnel_counts AS (
    SELECT
        COUNT(DISTINCT candidate_id) AS total_applications,
        -- Candidates who passed Application stage (and thus 'entered' Screening)
        SUM(CASE WHEN application_status = 'Passed' THEN 1 ELSE 0 END) AS passed_application,
        -- Candidates who passed Screening stage (and thus 'entered' Technical)
        SUM(CASE WHEN application_status = 'Passed' AND screening_status = 'Passed' THEN 1 ELSE 0 END) AS passed_screening,
        -- Candidates who passed Technical stage (and thus 'entered' Onsite)
        SUM(CASE WHEN application_status = 'Passed' AND screening_status = 'Passed' AND technical_status = 'Passed' THEN 1 ELSE 0 END) AS passed_technical,
        -- Candidates who passed Onsite stage (and thus 'entered' Offer negotiation)
        SUM(CASE WHEN application_status = 'Passed' AND screening_status = 'Passed' AND technical_status = 'Passed' AND onsite_status = 'Passed' THEN 1 ELSE 0 END) AS passed_onsite,
        -- Candidates who accepted the offer (final conversion)
        SUM(CASE WHEN application_status = 'Passed' AND screening_status = 'Passed' AND technical_status = 'Passed' AND onsite_status = 'Passed' AND offer_status = 'Accepted' THEN 1 ELSE 0 END) AS accepted_offer
    FROM
        candidate_funnel
)
SELECT
    'Application' AS stage_name,
    total_applications AS candidates_entered,
    passed_application AS candidates_passed_to_next_stage,
    ROUND(CAST(passed_application AS DECIMAL) / total_applications, 4) AS conversion_rate,
    ROUND(1 - (CAST(passed_application AS DECIMAL) / total_applications), 4) AS drop_off_rate
FROM funnel_counts
UNION ALL
SELECT
    'Screening' AS stage_name,
    passed_application AS candidates_entered,
    passed_screening AS candidates_passed_to_next_stage,
    CASE WHEN passed_application > 0 THEN ROUND(CAST(passed_screening AS DECIMAL) / passed_application, 4) ELSE 0 END AS conversion_rate,
    CASE WHEN passed_application > 0 THEN ROUND(1 - (CAST(passed_screening AS DECIMAL) / passed_application), 4) ELSE 1 END AS drop_off_rate
FROM funnel_counts
UNION ALL
SELECT
    'Technical' AS stage_name,
    passed_screening AS candidates_entered,
    passed_technical AS candidates_passed_to_next_stage,
    CASE WHEN passed_screening > 0 THEN ROUND(CAST(passed_technical AS DECIMAL) / passed_screening, 4) ELSE 0 END AS conversion_rate,
    CASE WHEN passed_screening > 0 THEN ROUND(1 - (CAST(passed_technical AS DECIMAL) / passed_screening), 4) ELSE 1 END AS drop_off_rate
FROM funnel_counts
UNION ALL
SELECT
    'Onsite' AS stage_name,
    passed_technical AS candidates_entered,
    passed_onsite AS candidates_passed_to_next_stage,
    CASE WHEN passed_technical > 0 THEN ROUND(CAST(passed_onsite AS DECIMAL) / passed_technical, 4) ELSE 0 END AS conversion_rate,
    CASE WHEN passed_technical > 0 THEN ROUND(1 - (CAST(passed_onsite AS DECIMAL) / passed_technical), 4) ELSE 1 END AS drop_off_rate
FROM funnel_counts
UNION ALL
SELECT
    'Offer' AS stage_name,
    passed_onsite AS candidates_entered,
    accepted_offer AS candidates_passed_to_next_stage,
    CASE WHEN passed_onsite > 0 THEN ROUND(CAST(accepted_offer AS DECIMAL) / passed_onsite, 4) ELSE 0 END AS conversion_rate,
    CASE WHEN passed_onsite > 0 THEN ROUND(1 - (CAST(accepted_offer AS DECIMAL) / passed_onsite), 4) ELSE 1 END AS drop_off_rate
FROM funnel_counts
ORDER BY
    CASE stage_name
        WHEN 'Application' THEN 1
        WHEN 'Screening' THEN 2
        WHEN 'Technical' THEN 3
        WHEN 'Onsite' THEN 4
        WHEN 'Offer' THEN 5
    END;