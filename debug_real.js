const puppeteer = require('puppeteer');
(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  
  await page.goto('http://127.0.0.1:5000');
  await new Promise(r => setTimeout(r, 2000));
  
  await page.evaluate(async () => {
    try {
      console.log("Clicking Table 3...");
      // Find table card with text "Masa 3"
      const tables = Array.from(document.querySelectorAll('.table-card'));
      const table3 = tables.find(t => t.innerText.includes('Masa 3'));
      if (table3) {
          table3.click();
      } else {
          console.log("Table 3 not found");
      }
      
      await new Promise(r => setTimeout(r, 1000));
      
      console.log("Current Order Items:", currentOrder ? currentOrder.items.length : 'No Order');
      
      console.log("Clicking Adisyonu Böl...");
      const btnSplit = Array.from(document.querySelectorAll('.btn')).find(b => b.innerText.includes('Adisyonu Böl'));
      if (btnSplit) {
          btnSplit.click();
      } else {
          console.log("Adisyonu Böl button not found");
      }
      
      await new Promise(r => setTimeout(r, 1000));
      
      console.log("Checking if modal is visible...");
      const modal = document.getElementById('itemSplitModal');
      console.log("Modal display:", modal.style.display);
      
      const plusBtn = document.querySelector('#itemSplitList button[onclick="changeSplitQty(this, 1)"]');
      if (plusBtn) {
          console.log("Clicking + button...");
          plusBtn.click();
      } else {
          console.log("+ button not found in modal");
      }
      
      console.log("Clicking Seçilenleri Yeni Bölüme Aktar...");
      const actBtn = document.querySelector('#itemSplitModal .btn-success');
      if (actBtn) {
          actBtn.click();
      } else {
          console.log("Action button not found");
      }
      
    } catch(e) {
      console.log("Exception:", e.toString());
    }
  });
  
  await new Promise(r => setTimeout(r, 2000));
  await browser.close();
})();
