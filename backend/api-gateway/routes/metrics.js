const express = require('express');
const router = express.Router();
const auth = require('../middleware/auth');
const WellnessMetric = require('../models/WellnessMetric');

/**
 * @route POST /api/v1/metrics/ingest
 * @desc Submit a wellness metric
 */
router.post('/ingest', auth, async (req, res) => {
  const { metric_type, value, source, quality_score, metadata } = req.body;
  const user_id = req.user.user.id;

  try {
    const metric = await WellnessMetric.add({
      user_id,
      metric_type,
      value,
      source,
      quality_score,
      metadata
    });

    res.status(201).json({
      message: 'Metric recorded successfully',
      metric,
      disclaimer: 'General Wellness Tracking: Not for medical diagnosis.'
    });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

/**
 * @route GET /api/v1/metrics/history
 * @desc Get user metric history
 */
router.get('/history', auth, async (req, res) => {
  const { type, limit } = req.query;
  const user_id = req.user.user.id;

  if (!type) {
    return res.status(400).json({ message: 'Metric type is required' });
  }

  try {
    const history = await WellnessMetric.getHistory(user_id, type, parseInt(limit) || 50);
    res.json({
      user_id,
      metric_type: type,
      history,
      disclaimer: 'Educational history for personal wellness tracking.'
    });
  } catch (err) {
    console.error(err.message);
    res.status(500).send('Server Error');
  }
});

module.exports = router;
