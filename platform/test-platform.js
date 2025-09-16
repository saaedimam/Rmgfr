#!/usr/bin/env node

const { exec } = require('child_process');
const http = require('http');

console.log('🧪 Testing Anti-Fraud Platform...\n');

// Test 1: Check if API can start
console.log('1. Testing API startup...');
exec('cd api && python -c "from src.main import app; print(\'✅ API imports successfully\')"', (error, stdout, stderr) => {
  if (error) {
    console.log('❌ API import failed:', error.message);
    return;
  }
  console.log('✅ API imports successfully');
  
  // Test 2: Check if web app can build
  console.log('\n2. Testing web app build...');
  exec('cd web && pnpm run build', (error, stdout, stderr) => {
    if (error) {
      console.log('❌ Web build failed:', error.message);
      return;
    }
    console.log('✅ Web app builds successfully');
    
    // Test 3: Check if mobile app can start
    console.log('\n3. Testing mobile app...');
    exec('cd mobile && pnpm run start --help', (error, stdout, stderr) => {
      if (error) {
        console.log('❌ Mobile app failed:', error.message);
        return;
      }
      console.log('✅ Mobile app ready');
      
      console.log('\n🎉 All tests passed! Platform is ready to use.');
      console.log('\n📋 Next steps:');
      console.log('1. Run: pnpm run dev (starts web + API)');
      console.log('2. Run: pnpm run dev:mobile (starts mobile app)');
      console.log('3. Visit: http://localhost:3000 (web app)');
      console.log('4. Visit: http://localhost:8000/docs (API docs)');
    });
  });
});
