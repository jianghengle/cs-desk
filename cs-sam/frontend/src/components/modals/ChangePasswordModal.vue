<template>
  <div class="modal" :class="{'is-active': opened}">
    <div class="modal-background"></div>
    <div class="modal-card">
      <header class="modal-card-head">
        <p class="modal-card-title">Change password</p>
        <button class="delete" @click="close"></button>
      </header>
      <section class="modal-card-body">
        <div class="field">
          <label class="label">New password</label>
          <div class="control">
            <input class="input" :class="{'is-danger': !newPasswordValid}" type="password" v-model="newPassword">
          </div>
        </div>
        <div class="field">
          <label class="label">New password again</label>
          <div class="control">
            <input class="input" type="password" :class="{'is-danger': !newPasswordAgainSame}" v-model="newPasswordAgain">
          </div>
        </div>
        <div v-if="error" class="notification is-danger is-light mt-5">
          <button class="delete" @click="error=''"></button>
          {{error}}
        </div>
        <div v-if="success" class="notification is-success is-light mt-5">
          <button class="delete" @click="success=''"></button>
          {{success}}
        </div>
      </section>
      <footer class="modal-card-foot">
        <div class="buttons">
          <a class="button is-link" :disabled="!newPasswordValid || !newPasswordAgainSame" :class="{'is-loading': waiting}" @click="submit">Submit</a>
          <a class="button" @click="close">Close</a>
        </div>
      </footer>
    </div>
  </div>
</template>

<script>
export default {
  name: 'change-password-modal',
  props: ['opened'],
  data () {
    return {
      waiting: false,
      error: '',
      success: '',
      newPassword: '',
      newPasswordAgain: '',
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    token () {
      return this.$store.state.user.token
    },
    adminPrefix () {
      return this.$store.state.config.adminPrefix
    },
    tableModel () {
      return this.$route.params.tableModel
    },
    itemId () {
      return this.$route.params.itemId
    },
    newPasswordValid () {
      var password = this.newPassword.trim()
      return password.length >= 8
    },
    newPasswordAgainSame () {
      return this.newPassword.trim() == this.newPasswordAgain.trim()
    },
  },
  methods: {
    close(){
      this.$emit('closeChangePasswordModal')
    },
    submit () {
      if (!this.newPasswordValid || !this.newPasswordAgainSame) {
        return
      }
      this.waiting = true
      this.error = ''
      this.success = ''
      this.newPassword
      var message = {
        password: this.newPassword.trim(),
      }
      this.$http.post(this.server + this.adminPrefix + this.tableModel + '/update-item/' + this.itemId, message).then(resp => {
        this.error = ''
        this.success = 'You have changed the password successfully.'
        this.waiting = false
      }, err => {
        this.error = err.body
        this.waiting = false
      })
    },
  },
}
</script>
