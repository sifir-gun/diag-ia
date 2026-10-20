-- Requêtes d'audit. Remplace wengraf-diag-ia si ton projet porte un autre nom.

-- 1. Retrouver un diagnostic et tous les événements journalisés qui le concernent.
DECLARE diag_id STRING DEFAULT 'COLLE_ICI_UNE_REFERENCE';
SELECT
  d.diagnostic_id, d.created_at, d.score, d.maturity_label, d.model,
  d.prompt_version, d.cost_usd, d.record_sha256,
  l.timestamp AS log_time, l.severity, l.jsonPayload.event AS event,
  l.jsonPayload.latency_ms AS log_latency_ms
FROM `wengraf-diag-ia.diagnostic.diagnostics` AS d
LEFT JOIN `wengraf-diag-ia.audit_logs.run_googleapis_com_stdout` AS l
  ON l.jsonPayload.diagnostic_id = d.diagnostic_id
WHERE d.diagnostic_id = diag_id
ORDER BY log_time;

-- 2. Volume, coût et latence par jour (source du tableau de bord Looker Studio).
SELECT
  DATE(created_at) AS jour,
  COUNT(*) AS diagnostics,
  ROUND(AVG(score), 1) AS score_moyen,
  ROUND(SUM(cost_usd), 4) AS cout_total_usd,
  ROUND(AVG(cost_usd), 5) AS cout_moyen_usd,
  APPROX_QUANTILES(latency_ms, 100)[OFFSET(95)] AS latence_p95_ms
FROM `wengraf-diag-ia.diagnostic.diagnostics`
GROUP BY jour
ORDER BY jour DESC;

-- 3. Incidents : appels au modèle ou enregistrements en échec.
SELECT timestamp, severity, jsonPayload.event AS event, jsonPayload.diagnostic_id AS diagnostic_id
FROM `wengraf-diag-ia.audit_logs.run_googleapis_com_stdout`
WHERE jsonPayload.event IN ('llm_call_failed', 'llm_output_rejected', 'storage_failed')
ORDER BY timestamp DESC
LIMIT 100;
