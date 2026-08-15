const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  
  await page.goto('http://127.0.0.1:5000');
  await new Promise(r => setTimeout(r, 2000));
  
  await page.evaluate(async () => {
    try {
      window.currentOrder = {
          id: 9999,
          items: [
              { id: 1, quantity: 2, price: 100, product_name: 'Test', is_complimentary: false }
          ]
      };
      
      openItemSplitModal();
      
      const inp = document.querySelector('.item-split-qty');
      console.log("Input initial value:", inp ? inp.value : 'none');
      
      const plusBtn = document.querySelector('button[onclick*="changeSplitQty"]');
      if (plusBtn) {
          console.log("Found button, clicking...");
          plusBtn.click();
          console.log("Input after click:", inp.value);
      } else {
          console.log("Could not find button");
      }
      
    } catch(e) {
      console.log("Exception:", e.toString());
    }
  });
  
  await new Promise(r => setTimeout(r, 1000));
  await browser.close();
})();
