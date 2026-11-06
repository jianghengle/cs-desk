<template>
  <div>
    <nav class="navbar has-shadow" role="navigation" aria-label="main navigation">
      <div class="container p-3">
        <div class="navbar-brand">
          <router-link class="navbar-item is-size-4 has-text-weight-bold" :to="'/'">
            Serverless Django
          </router-link>
          

          <a role="button" class="navbar-burger" aria-label="menu" aria-expanded="false"
            :class="{'is-active': menuActive}" @click="menuActive = !menuActive">
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
            <span aria-hidden="true"></span>
          </a>
        </div>

        <div id="navbarBasicExample" class="navbar-menu"  :class="{'is-active': menuActive}">
          <div class="navbar-start">
          </div>

          <div class="navbar-end">
            <div class="navbar-item has-dropdown is-hoverable" v-if="isAdmin">
              <a class="navbar-link">
                <span class="icon">
                  <i class="fas fa-tools"></i>
                </span>
              </a>
              <div class="navbar-dropdown">
                <router-link :to="'/admin'" class="navbar-item">
                  <span>Admin</span>
                </router-link>
                <router-link :to="'/admin/call-apis'" class="navbar-item">
                  <span>Call APIs</span>
                </router-link>
                <router-link :to="'/admin/ai-agent'" class="navbar-item">
                  <span>AI Agent</span>
                </router-link>
              </div>
            </div>
            <div class="navbar-item has-dropdown is-hoverable" v-if="token">
              <a class="navbar-link">
                <span class="icon">
                  <i class="fas fa-user"></i>
                </span>
                <span v-if="username">{{ username }}</span>
              </a>

              <div class="navbar-dropdown">
                <a class="navbar-item" @click="signout">
                  <span>Sign out</span>
                </a>
              </div>
            </div>
          </div>
        </div>
      </div>
    </nav>
  </div>
</template>

<script>
import Vue from 'vue'

export default {
  name: 'my-header',
  data () {
    return {
      menuActive: false
    }
  },
  computed: {
    token () {
      return this.$store.state.user.token
    },
    username () {
      return this.$store.state.user.username
    },
    isAdmin () {
      return this.$store.state.user.isAdmin
    },
    routerPath () {
      return this.$route.path
    },
    server () {
      return this.$store.state.config.server
    },
  },
  methods: {
    signout () {
      this.$store.commit('user/reset')
      if (this.routerPath != '/admin') {
        this.$router.push('/admin')
      }
    },
    verifyToken () {
      var message = {
        token: this.token,
      }
      this.$http.post(this.server + '/api/user/verify-token/', message).then(resp => {
        var user = resp.body
        user.token = this.token
        this.$store.commit('user/setUser', user)
      }, err => {
        this.error = err.body
        this.$store.commit('user/reset')
        if (this.routerPath != '/admin') {
          this.$router.push('/admin')
        }
      })
    },
  },
  mounted () {
    if (this.token) {
      Vue.http.headers.common['Authorization'] = this.token
      this.verifyToken()
    }
  }
}
</script>
