import { defineConfig } from '@playwright/test';
export default defineConfig({
  testDir: './tests',
  timeout: 120000,
  workers: 1,
  use: {baseURL:'http://127.0.0.1:5174',viewport:{width:1440,height:1000},headless:true,
    launchOptions:{channel:'msedge',args:['--enable-webgl','--ignore-gpu-blocklist']},
  },
  reporter: [['list']],
  webServer:{command:'npm run dev',url:'http://127.0.0.1:5174',reuseExistingServer:true,timeout:30000},
});
