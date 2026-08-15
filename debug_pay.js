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
  
  await page.evaluate(async () => {
    try {
      window.currentOrder = { id: 1106, items: [], total: 500 };
      window.payEntries = [];
      
      console.log("Calling splitRemaining(2)...");
      splitRemaining(2);
      
      console.log("Input value:", document.getElementById('payEntryAmount').value);
      
      console.log("Clicking Nakit...");
      const btn = Array.from(document.querySelectorAll('button')).find(b => b.textContent.includes('NAKİT'));
      if (btn) btn.click();
      else console.log("Nakit not found");
      
      console.log("Pay entries:", JSON.stringify(payEntries));
    } catch (e) {
      console.log("EXCEPTION:", e.message);
    }
  });
  
  await new Promise(r => setTimeout(r, 1000));
  await browser.close();
})();
