const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', err => console.log('PAGE ERROR:', err.toString()));
  await page.goto('http://127.0.0.1:5000');
  await new Promise(r => setTimeout(r, 2000));
  
  await page.evaluate(async () => {
    try {
      // Create a fake order
      window.currentOrder = {
          id: 1106,
          items: [
              { id: 1, quantity: 2, price: 100, product_name: 'Test', is_complimentary: false }
          ]
      };
      
      console.log("Calling openItemSplitModal...");
      openItemSplitModal();
      
      console.log("Waiting a bit...");
      await new Promise(r => setTimeout(r, 500));
      
      console.log("Clicking + button...");
      const plusBtn = document.querySelector('#itemSplitList button:nth-child(3)');
      if (plusBtn) plusBtn.click();
      else console.log("+ button not found");
      
      console.log("Clicking Seçilenleri Yeni Bölüme Aktar...");
      const actBtn = document.querySelector('#itemSplitModal .btn-success');
      if (actBtn) actBtn.click();
      else console.log("Action button not found");
      
    } catch(e) {
      console.log("Exception:", e.toString());
    }
  });
  
  await new Promise(r => setTimeout(r, 2000));
  await browser.close();
})();
