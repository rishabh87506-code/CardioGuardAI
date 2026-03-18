const db = require('./config/db');
db.query('SELECT NOW()')
  .then(res => {
    console.log('DB Connection OK:', res.rows[0]);
    process.exit(0);
  })
  .catch(err => {
    console.error('DB Connection Failed:', err);
    process.exit(1);
  });
