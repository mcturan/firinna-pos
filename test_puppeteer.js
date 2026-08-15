const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  await page.goto('http://127.0.0.1:5000');
  
  try {
      await page.waitForSelector('.blueprint-table', { timeout: 5000 });
      const grids = await page.$$('.blueprint-table');
      if (grids.length > 0) {
          console.log('Clicking table to open...');
          await grids[1].click();
          await new Promise(r => setTimeout(r, 1000));
          
          console.log('Adding product...');
          const products = await page.$$('.product-card');
          if (products.length > 0) {
              await products[0].click();
              await new Promise(r => setTimeout(r, 1000));
          }
          
          console.log('Clicking checkout...');
          await page.evaluate(() => {
              if (typeof openPaymentModal === 'function') openPaymentModal();
              else console.log('openPaymentModal is not a function');
          });
          await new Promise(r => setTimeout(r, 1500));
          
          console.log('Clicking completePayment...');
          await page.evaluate(() => {
              completePayment();
          });
          await new Promise(r => setTimeout(r, 1000));
      }
  } catch(e) {
      console.log('EVAL ERROR:', e);
  }
  await browser.close();
})();
