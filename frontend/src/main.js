// Rakenduse algus: loob Vue rakenduse, lisab ruuteri ja paneb selle index.html-i <div id="app"> sisse.
import { createApp } from 'vue'

import App from './App.vue'
import router from './router.js'
import './style.css'

createApp(App).use(router).mount('#app')
