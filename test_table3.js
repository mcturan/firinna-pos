const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({ args: ['--no-sandbox'] });
  const page = await browser.newPage();
  
  page.on('console', msg => console.log('PAGE LOG:', msg.text()));
  page.on('pageerror', error => console.log('PAGE ERROR:', error.message));
  
  await page.goto('http://127.0.0.1:5000');
  await new Promise(r => setTimeout(r, 1000));
  
  try {
      // Find Table 3
      console.log('Evaluating Table 3 click...');
      await page.evaluate(() => {
          const t3 = Array.from(document.querySelectorAll('.blueprint-table')).find(el => el.textContent.includes('3'));
          if (t3) {
              console.log('Found Table 3, clicking...');
              t3.click();
          } else {
              console.log('Table 3 NOT FOUND!');
          }
      });
      
      await new Promise(r => setTimeout(r, 1000));
      
      const modalVisible = await page.evaluate(() => {
          const m = document.getElementById('orderModal');
          return m ? m.style.display : 'NO MODAL';
      });
      console.log('orderModal display:', modalVisible);
      
  } catch(e) {
      console.log('SCRIPT ERROR:', e);
  }
  
  await browser.close();
})();
