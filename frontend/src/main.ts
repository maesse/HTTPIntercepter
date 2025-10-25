import './assets/main.css'
import { createApp } from 'vue'
import { createPinia } from 'pinia'
import App from './App.vue'
import router from './router'
// Vuetify setup
import 'vuetify/styles'
import { createVuetify } from 'vuetify'
import { aliases, mdi } from 'vuetify/iconsets/mdi'
import '@mdi/font/css/materialdesignicons.css'

const vuetify = createVuetify({
	theme: {
		defaultTheme: 'light',
		themes: {
			light: { dark: false },
			dark: { dark: true },
		},
	},
	icons: {
		defaultSet: 'mdi',
		aliases,
		sets: { mdi },
	},
})

const app = createApp(App)

app.use(createPinia())
app.use(router)
app.use(vuetify)

app.mount('#app')
