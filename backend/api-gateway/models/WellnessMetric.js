const db = require('../config/db');

const WellnessMetric = {
  /**
   * Add a new wellness metric
   */
  async add({ user_id, metric_type, value, source, quality_score, metadata }) {
    const query = `
      INSERT INTO wellness_metrics (user_id, metric_type, source, measurement_timestamp, quality_score, metadata)
      VALUES ($1, $2, $3, NOW(), $4, $5)
      RETURNING *;
    `;
    const values = [user_id, metric_type, source, quality_score, JSON.stringify(metadata)];
    const { rows } = await db.query(query, values);
    return rows[0];
  },

  /**
   * Get user's metric history
   */
  async getHistory(user_id, metric_type, limit = 50) {
    const query = `
      SELECT * FROM wellness_metrics 
      WHERE user_id = $1 AND metric_type = $2 
      ORDER BY measurement_timestamp DESC 
      LIMIT $3;
    `;
    const { rows } = await db.query(query, [user_id, metric_type, limit]);
    return rows;
  }
};

module.exports = WellnessMetric;
