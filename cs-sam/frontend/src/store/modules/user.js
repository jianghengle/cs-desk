// initial state

export const state = {
  token: localStorage.getItem('token'),
  email: localStorage.getItem('email'),
  username: localStorage.getItem('username'),
  groups: localStorage.getItem('groups') ? JSON.parse(localStorage.getItem('groups')) : null,
  isAdmin: localStorage.getItem('isAdmin') == 'true',
}
 
// mutations
export const mutations = {
  setUser (state, user) {
    state.token = user.token
    state.email = user.email
    state.username = user.username
    state.groups = user.groups
    state.isAdmin = user.isAdmin
    localStorage.setItem('token', user.token)
    localStorage.setItem('email', user.email)
    localStorage.setItem('username', user.username)
    localStorage.setItem('groups', JSON.stringify(user.groups))
    localStorage.setItem('isAdmin', JSON.stringify(user.isAdmin))
  },


  reset (state) {
    state.token = null
    state.email = null
    state.username = null
    state.groups = null
    state.isAdmin = null
    localStorage.removeItem('token')
    localStorage.removeItem('email')
    localStorage.removeItem('username')
    localStorage.removeItem('groups')
    localStorage.removeItem('isAdmin')
  },
}

export default {
  namespaced: true,
  state,
  mutations
}
