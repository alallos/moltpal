const fs = require('fs');
const path = require('path');
const db = require('./index');

async function migrate() {
  try {
    console.log('🔧 Running database migrations...');
    
    const schema = fs.readFileSync(
      path.join(__dirname, 'schema.sql'),
      'utf8'
    );
    
    await db.query(schema);
    
    console.log('✅ Database migrations completed successfully');
    process.exit(0);
  } catch (error) {
    console.error('❌ Migration failed:', error);
    process.exit(1);
  }
}

migrate();
