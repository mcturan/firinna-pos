const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.toString()));
  await page.goto('http://127.0.0.1:5000');
  await new Promise(r => setTimeout(r, 2000));
  
  // Try to call openItemSplitModal directly
  await page.evaluate(() => {
    try {
      openItemSplitModal();
      console.log("openItemSplitModal executed");
    } catch(e) {
      console.log("Error calling openItemSplitModal:", e.toString());
    }
  });
  
  await browser.close();
})();
