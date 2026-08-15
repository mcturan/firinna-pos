const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  await page.goto('http://127.0.0.1:5000');
  await new Promise(r => setTimeout(r, 1000));
  
  try {
      const grids = await page.$$('.blueprint-table');
      if (grids.length > 0) {
          console.log('Clicking table...');
          await grids[2].click();
          await new Promise(r => setTimeout(r, 1000));
          
          // Let's add a product first
          const products = await page.$$('.product-card');
          if (products.length > 0) {
              await products[0].click();
              await new Promise(r => setTimeout(r, 1000));
          }
          
          console.log('Looking for Adisyonu Böl button...');
          // Check if button exists
          const btnHtml = await page.evaluate(() => {
              const b = Array.from(document.querySelectorAll('button')).find(el => el.textContent.includes('Adisyonu Böl'));
              if(b) return b.outerHTML;
              return 'NOT FOUND';
          });
          console.log('Button HTML:', btnHtml);
          
          // Try clicking it using JS
          console.log('Clicking Adisyonu Böl (via JS page.evaluate)...');
          await page.evaluate(() => {
              openItemSplitModal();
          });
          await new Promise(r => setTimeout(r, 1000));
          
          // Check if itemSplitModal is visible
          const modalVisible = await page.evaluate(() => {
              const m = document.getElementById('itemSplitModal');
              return m ? m.style.display : 'NO MODAL';
          });
          console.log('itemSplitModal display:', modalVisible);
          
          if(modalVisible === 'flex' || modalVisible === 'block') {
              console.log('Modal opened successfully. Now selecting item...');
              await page.evaluate(() => {
                  const inputs = document.querySelectorAll('.item-split-qty');
                  if (inputs.length > 0) {
                      inputs[0].value = 1;
                      recalcItemSplitTotal();
                  }
              });
              
              await new Promise(r => setTimeout(r, 500));
              
              console.log('Clicking applyItemSplit...');
              await page.evaluate(() => {
                  applyItemSplit();
              });
              
              await new Promise(r => setTimeout(r, 1000));
              
              // Check toast messages
              const toasts = await page.evaluate(() => {
                  const t = document.getElementById('toast-container');
                  return t ? t.innerText : 'NO TOAST CONTAINER';
              });
              console.log('Toasts:', toasts);
          }
      }
  } catch(e) {
      console.log('SCRIPT ERROR:', e);
  }
  
  await browser.close();
})();
