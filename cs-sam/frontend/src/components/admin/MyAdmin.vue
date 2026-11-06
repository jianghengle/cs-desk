<template>
  <div class="container my-page-body">
    <section class="section" v-if="!token">
      <h1 class="title is-5">SAM Admin</h1>
      <h2 class="subtitle is-6 mt-2">
        Please sign in manage your data.
      </h2>

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

    <div v-if="token" class="p-3">
      <div v-if="isAdmin">
        <nav class="breadcrumb" aria-label="breadcrumbs">
          <ul>
            <li class="is-active">
              <router-link :to="'/admin'" aria-current="page">Tables</router-link>
            </li>
          </ul>
        </nav>

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

          <div class="box" v-for="(table, i) in tables" :key="'table-'+i">
            <article class="media">
              <div class="media-left">
                <span>
                  <i class="fas fa-table"></i>
                </span>
              </div>
              <div class="media-content">
                <div class="content">
                  <p>
                    <router-link :to="'/admin/table/' + table.modelName">
                      <strong>{{ table.tableName }}</strong>
                    </router-link><br/>
                    <small>Items: {{ table.metadata.itemCount }}</small>
                  </p>
                </div>
              </div>
            </article>
          </div>
        </div>
      </div>
      <div v-else>
        <div v-if="error" class="notification is-warning is-light">
          You are not admin to access this page.
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import Vue from 'vue'

export default {
  name: 'my-admin',
  components: {
  },
  data () {
    return {
      waiting: false,
      error: '',
      email: '',
      password: '',
      tables: null,
    }
  },
  computed: {
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
        } else {
          this.error = 'Failed to sign in!'
          this.$store.commit('user/reset')
        }
        this.waiting = false
        this.getTables()
      }, err => {
        this.error = err.body
        this.waiting = false
      })
    },
    getTables () {
      this.waiting = true
      this.$http.get(this.server + this.adminPrefix + 'get-tables').then(resp => {
        this.tables = resp.body
        this.waiting = false
      }, err => {
        this.error = err.body
        this.waiting = false
      })
    },
    openTable (table) {
      this.$router.push('/admin/table/' + table.modelName)
    },
  },
  mounted () {
    this.$nextTick(() => {
      if (this.token) {
        this.getTables()
      }
    })
  }
}
</script>

<style scoped>
.name-input {
  max-width: 600px;
}
</style>
