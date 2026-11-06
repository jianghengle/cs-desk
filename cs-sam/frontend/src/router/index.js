import Vue from 'vue'
import VueRouter from 'vue-router'
import MyHome from '../views/MyHome.vue'
import MyAdmin from '../components/admin/MyAdmin.vue'
import AdminTable from '../components/admin/AdminTable.vue'
import AdminTableItem from '../components/admin/AdminTableItem.vue'
import CallAPIs from '../components/admin/CallAPIs.vue'
import AdminChat from '../components/admin/AdminChat.vue'

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
    {
      path: '/admin/ai-agent',
      name: 'AdminChat',
      component: AdminChat
    },
  ]
})

export default router
