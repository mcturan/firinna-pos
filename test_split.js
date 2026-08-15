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
          await grids[2].click();
          await new Promise(r => setTimeout(r, 1000));
          
          console.log('Adding product...');
          const products = await page.$$('.product-card');
          if (products.length > 0) {
              await products[0].click();
              await new Promise(r => setTimeout(r, 1000));
          }
          
          console.log('Clicking Adisyonu Böl...');
          await page.evaluate(() => openItemSplitModal());
          await new Promise(r => setTimeout(r, 1500));
          
          console.log('Selecting items to split...');
          await page.evaluate(() => {
              const inputs = document.querySelectorAll('.item-split-qty');
              if (inputs.length > 0) {
                  inputs[0].value = 1; // Split 1 item
              }
          });
          await new Promise(r => setTimeout(r, 500));
          
          console.log('Clicking Böl ve Yeni Adisyon Aç...');
          await page.evaluate(() => applyItemSplit());
          await new Promise(r => setTimeout(r, 1500));
          
      }
  } catch(e) {
      console.log('EVAL ERROR:', e);
  }
  await browser.close();
})();
