const jwt = require('jsonwebtoken');

const auth = (req, res, next) => {
  const token = req.header('Authorization')?.replace('Bearer ', '');

  if (!token) {
    return res.status(401).json({ 
      message: 'No authentication token, access denied',
      disclaimer: 'This is a general wellness platform. Security is prioritized for your data privacy.'
    });
  }

  try {
    const decoded = jwt.verify(token, process.env.JWT_SECRET);
    req.user = decoded;
    next();
  } catch (err) {
    res.status(401).json({ 
      message: 'Token is invalid or expired',
      error: err.message
    });
  }
};

module.exports = auth;
