const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  
  const errors = [];
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => {
      console.log('PAGE ERROR:', err.toString());
      errors.push(err.toString());
  });
  
  await page.goto('http://127.0.0.1:5000');
  await new Promise(r => setTimeout(r, 2000));
  
  console.log("Total errors:", errors.length);
  
  await browser.close();
})();
