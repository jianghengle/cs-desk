import Vue from 'vue'

import App from './App.vue'
import router from './router'
import store from './store'

import 'bulma/css/bulma.css'

import VueResource from 'vue-resource'
Vue.use(VueResource)

import ECharts from 'vue-echarts'
import { use, registerTheme } from 'echarts/core'

// import ECharts modules manually to reduce bundle size
import {
  CanvasRenderer
} from 'echarts/renderers'
import {
  LineChart,
  BarChart,
  PieChart,
} from 'echarts/charts'
import {
  TitleComponent,
  GridComponent,
  TooltipComponent,
  LegendComponent,
  ToolboxComponent,
  DataZoomComponent,
  DataZoomInsideComponent,
  DataZoomSliderComponent,
  MarkPointComponent
} from 'echarts/components'

use([
  LineChart,
  CanvasRenderer,
  BarChart,
  PieChart,
  GridComponent,
  TooltipComponent,
  TitleComponent,
  LegendComponent,
  ToolboxComponent,
  DataZoomComponent,
  DataZoomInsideComponent,
  DataZoomSliderComponent,
  MarkPointComponent
]);

// register globally (or you can do it locally)
Vue.component('v-chart', ECharts)

new Vue({
  router,
  store,
  render: (h) => h(App)
}).$mount('#app')
