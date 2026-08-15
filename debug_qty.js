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
          id: 1106,
          items: [
              { id: 1, quantity: 2, price: 100, product_name: 'Test', is_complimentary: false }
          ]
      };
      
      openItemSplitModal();
      await new Promise(r => setTimeout(r, 100));
      
      const input = document.querySelector('.item-split-qty');
      console.log("Input initial value:", input ? input.value : "NOT FOUND");
      
      const plus = document.querySelector('button[onclick="changeSplitQty(this, 1)"]');
      if (plus) {
          console.log("Clicking + button...");
          plus.click();
          console.log("Input after + click:", input.value);
      } else {
          console.log("+ button not found");
      }
      
    } catch(e) {
      console.log("Exception:", e.toString());
    }
  });
  
  await browser.close();
})();
