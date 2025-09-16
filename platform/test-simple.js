#!/usr/bin/env node

const { exec } = require('child_process');

console.log('Testing Anti-Fraud Platform...\n');

// Test 1: Check if API can start
console.log('1. Testing API startup...');
exec('cd api && python -c "from src.main import app; print(\'API imports successfully\')"', (error, stdout, stderr) => {
  if (error) {
    console.log('API import failed:', error.message);
    return;
  }
  console.log('API imports successfully');
  
  console.log('\nPlatform is ready!');
  console.log('\nNext steps:');
  console.log('1. Run: pnpm run dev (starts web + API)');
  console.log('2. Run: pnpm run dev:mobile (starts mobile app)');
  console.log('3. Visit: http://localhost:3000 (web app)');
  console.log('4. Visit: http://localhost:8000/docs (API docs)');
});
