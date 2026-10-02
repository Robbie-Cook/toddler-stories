const puppeteer = require('puppeteer');

(async () => {
  const browser = await puppeteer.launch({headless: true, args: ['--no-sandbox']});
  const page = await browser.newPage();
  await page.setViewport({width: 390, height: 800});
  await page.goto('http://localhost:8765/#song/twinkle-twinkle', {waitUntil: 'networkidle0'});
  await page.screenshot({path: '/tmp/before-song.png'});
  console.log('Screenshot saved to /tmp/before-song.png');
  await browser.close();
})();
