const dev = process.env.NODE_ENV == 'development'

// initial state
export const state = {
  server: dev ? 'http://localhost:3000' : '/Prod',
  adminPrefix: '/api/admin/',
}

// mutations
export const mutations = {
}

export default {
  namespaced: true,
  state,
  mutations
}
