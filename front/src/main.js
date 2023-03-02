import Vue from 'vue'
import * as Sentry from "@sentry/vue";
import { BrowserTracing } from "@sentry/tracing";

import App from './App.vue'
import router from './router'
import store from '@/store/AuthenticationStore'
import vuetify from './plugins/vuetify'

import api from "@/services/api";




Vue.config.productionTip = false

Vue.prototype.$api = api; 
new Vue({
  router,
  store,
  vuetify,
  render: h => h(App)
}).$mount('#app')

Sentry.init({
  Vue,
  dsn: "https://13d8afae40734d11a61b2fd19a118d9e@o491089.ingest.sentry.io/5973964",
  integrations: [
    new BrowserTracing({
      routingInstrumentation: Sentry.vueRouterInstrumentation(router),
      tracingOrigins: ["webapp-zenscanner.znk.fr"],
    }),
  ],
  tracesSampleRate: 0.1,
});