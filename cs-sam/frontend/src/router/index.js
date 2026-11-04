import Vue from 'vue'
import VueRouter from 'vue-router'
import MyHome from '../views/MyHome.vue'
import MyAdmin from '../views/MyAdmin.vue'
import AdminTable from '../views/AdminTable.vue'
import AdminTableItem from '../views/AdminTableItem.vue'
import CallAPIs from '../views/CallAPIs.vue'

Vue.use(VueRouter)

const router = new VueRouter({
  mode: 'history',
  base: import.meta.env.BASE_URL,
  routes: [
    {
      path: '/',
      name: 'MyHome',
      component: MyHome
    },
    {
      path: '/admin',
      name: 'MyAdmin',
      component: MyAdmin
    },
    {
      path: '/admin/table/:tableModel',
      name: 'AdminTable',
      component: AdminTable
    },
    {
      path: '/admin/item/:tableModel/:itemId',
      name: 'AdminTableItem',
      component: AdminTableItem
    },
    {
      path: '/admin/call-apis',
      name: 'CallAPIs',
      component: CallAPIs
    },
  ]
})

export default router
