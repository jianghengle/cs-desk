<template>
  <div class="container my-page-body">
    <section class="section" v-if="!token">
      <h1 class="title is-5">CS Desktop</h1>

      <div class="field">
        <label class="label">Email</label>
        <div class="control has-icons-left has-icons-right">
          <input class="input" placeholder="Email" v-model="email">
          <span class="icon is-small is-left">
            <i class="fas fa-envelope"></i>
          </span>
        </div>
      </div>

      <div class="field">
        <label class="label">Password</label>
        <div class="control has-icons-left has-icons-right">
          <input class="input" type="password" placeholder="Password" v-model="password" @keyup.enter="signin">
          <span class="icon is-small is-left">
            <i class="fas fa-key"></i>
          </span>
        </div>
      </div>

      <div class="field is-grouped mt-5">
        <div class="control">
          <button class="button is-link" :disabled="!formValid" :class="{'is-loading': waiting}" @click="signin">Sign in</button>
        </div>
      </div>
    </section>

    <div class="mt-3 pb-6" v-if="token">
      <div class="mt-5">
        <div v-if="waiting">
          <span class="icon is-medium is-size-4">
            <i class="fas fa-spinner fa-pulse"></i>
          </span>
        </div>

        <div v-if="error" class="notification is-danger is-light">
          <button class="delete" @click="error=''"></button>
          {{error}}
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'

export default {
  name: 'my-home',
  components: {
  },
  data () {
    return {
      error: '',
      waiting: false,
      email: '',
      password: '',
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    token () {
      return this.$store.state.user.token
    },
    isAdmin () {
      return this.$store.state.user.isAdmin
    },
    server () {
      return this.$store.state.config.server
    },
    adminPrefix () {
      return this.$store.state.config.adminPrefix
    },
    emailValid () {
      var re = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
      return re.test(this.email.trim().toLowerCase())
    },
    formValid () {
      return this.emailValid && this.password
    },
  },
  methods: {
    signin () {
      if (this.waiting) {
        return
      }
      this.waiting = true
      this.email = this.email.trim().toLowerCase()
      var message = {email: this.email, password: this.password}
      this.$http.post(this.server + '/api/user/auth-user/', message).then(resp => {
        if (resp.body) {
          var user = resp.body
          Vue.http.headers.common['Authorization'] = user.token
          this.$store.commit('user/setUser', user)
          this.email = ''
          this.password = ''
          this.getTickets()
        } else {
          this.error = 'Failed to sign in!'
          this.$store.commit('user/reset')
        }
        this.waiting = false
      }, err => {
        this.error = err.body
        this.waiting = false
      })
    },
    getTickets () {
      this.waiting = true
      this.$http.get(this.server + '/api/ticket/get-tickets').then(resp => {
        this.tables = resp.body
        this.waiting = false
      }, err => {
        this.error = err.body
        this.waiting = false
      })
    },
  },
  mounted () {
    this.$nextTick(() => {
      if (this.token) {
        this.getTickets()
      }
    })
  },
}
</script>

<style scoped>

</style>
