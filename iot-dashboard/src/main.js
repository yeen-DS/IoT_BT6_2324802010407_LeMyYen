import { createApp } from "vue";
import { createPinia } from "pinia";
import { createRouter, createWebHistory } from "vue-router";
import ElementPlus from "element-plus";
import "element-plus/dist/index.css";

import App from "./App.vue";

import DashboardView from "./views/DashboardView.vue";
import DevicesView from "./views/DevicesView.vue";
import AlertsView from "./views/AlertsView.vue";
import SettingsView from "./views/SettingsView.vue";
import AIView
  from "./views/AIView.vue";

const router =
createRouter({

  history:
    createWebHistory(),

  routes: [

    {
      path: "/",
      component:
        DashboardView
    },

    {
      path: "/devices",
      component:
        DevicesView
    },

    {
      path: "/ai",
      component:
        AIView
    },

    {
      path: "/alerts",
      component:
        AlertsView
    },

    {
      path: "/settings",
      component:
        SettingsView
    }

  ]

});
createApp(App)
  .use(createPinia())
  .use(router)
  .use(ElementPlus)
  .mount("#app");