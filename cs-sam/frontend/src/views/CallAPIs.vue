<template>
  <div class="container my-page-body">
    <section class="section">
      <h1 class="title is-5">Call APIs</h1>
      <div class="field">
        <div class="control">
          <label class="checkbox">
            <input type="checkbox" v-model="isAdvanced">
            Advanced
          </label>
        </div>
      </div>

      <div class="field has-addons">
        <p class="control">
          <span class="select">
            <select v-model="method">
              <option>GET</option>
              <option>POST</option>
              <option>PUT</option>
              <option>PATCH</option>
              <option>DELETE</option>
            </select>
          </span>
        </p>
        <p class="control" v-if="isAdvanced">
          <input class="input" type="text" placeholder="http://domain:port" v-model="host">
        </p>
        <p class="control is-expanded">
          <input class="input" type="text" placeholder="/api/path" v-model="path">
        </p>
      </div>

      <div class="field" v-if="isAdvanced">
        <label class="label">Headers</label>
        <div class="control">
          <textarea class="textarea" :class="{'is-danger': !headersValid}" placeholder='{"content-type": "application/json"}' v-model="headers"></textarea>
        </div>
        <p class="help is-warning">Please make sure NOT to send your token to hosts other than yours!</p>
      </div>

      <div class="field" v-if="method != 'GET'">
        <label class="label">Payload</label>
        <div class="control">
          <textarea class="textarea" :class="{'is-danger': !payloadValid}" placeholder='{"id": "id"}' v-model="payload"></textarea>
        </div>
      </div>

      <div class="field is-grouped mt-5">
        <div class="control">
          <button class="button is-link" :disabled="!canCall" @click="callAPI" :class="{'is-loading': waiting}">Submit</button>
        </div>
        <div class="control">
          <button class="button" @click="resetHeaders">Reset headers</button>
        </div>
      </div>

      <div v-if="waiting">
        <span class="icon is-medium is-size-4">
          <i class="fas fa-spinner fa-pulse"></i>
        </span>
      </div>

      <div v-if="error" class="notification is-danger is-light">
        <button class="delete" @click="error=''"></button>
        {{error}}
      </div>

      <div class="field mt-5" v-if="resp">
        <label class="label">Response</label>
        <pre class="pre">{{ resp }}</pre>
      </div>

    </section>
  </div>
</template>

<script>
import axios from 'axios'

export default {
  name: 'call-aps',
  components: {
  },
  data () {
    return {
      error: '',
      waiting: false,
      isAdvanced: false,
      method: 'GET',
      path: '',
      host: '',
      headers: '',
      payload: '',
      resp: '',
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    token () {
      return this.$store.state.user.token
    },
    headersValid () {
      return this.checkJson(this.headers)
    },
    payloadValid () {
      return (!this.payload) || this.checkJson(this.payload)
    },
    canCall () {
      if (!this.headersValid) {
        return false
      }
      if (!this.path) {
        return false
      }
      if (this.method != 'GET' && !this.payloadValid) {
        return false
      }
      return true
    },
  },
  methods: {
    checkJson (s) {
      try {
        JSON.parse(s)
        return true
      } catch (e) {
        return false
      }
    },
    callAPI () {
      if (!this.canCall) {
        return
      }
      var method = this.method.toLowerCase()
      var url = this.path.trim()
      if (this.host) {
        url = this.host.trim() + url
      }
      var headers = JSON.parse(this.headers)
      var data = null
      if (this.method != 'GET') {
        data = JSON.parse(this.payload)
      }
      var vm = this
      axios({
        method: method,
        url: url,
        data: data,
        headers: headers,
      }).then(resp => {
        this.resp = JSON.stringify(resp.data, null, 2)
        this.waiting = false
      }, err => {
        this.error = err.body
      })
    },
    resetHeaders () {
      var headers = {
        Authorization: this.token
      }
      this.headers = JSON.stringify(headers, null, 2)
    },
  },
  mounted () {
    this.resetHeaders()
  },
}
</script>

<style scoped>

</style>
