const db = require('../config/db');
const bcrypt = require('bcryptjs');

const User = {
  /**
   * Create a new user
   */
  async create({ email, password, full_name, phone }) {
    const salt = await bcrypt.genSalt(10);
    const password_hash = await bcrypt.hash(password, salt);
    const tenant_id = '00000000-0000-0000-0000-000000000000'; // Default tenant

    const query = `
      INSERT INTO users (email, password_hash, full_name, phone_e164, tenant_id)
      VALUES ($1, $2, $3, $4, $5)
      RETURNING user_id, email, full_name, preferred_language;
    `;
    const values = [email, password_hash, full_name, phone, tenant_id];
    const { rows } = await db.query(query, values);
    return rows[0];
  },

  /**
   * Find user by email
   */
  async findByEmail(email) {
    const query = 'SELECT * FROM users WHERE email = $1';
    const { rows } = await db.query(query, [email]);
    return rows[0];
  },

  /**
   * Find user by ID
   */
  async findById(id) {
    const query = 'SELECT user_id, email, full_name, preferred_language FROM users WHERE user_id = $1';
    const { rows } = await db.query(query, [id]);
    return rows[0];
  }
};

module.exports = User;
