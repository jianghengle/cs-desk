<template>
  <div class="mt-4">
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
  </div>
</template>

<script>
export default {
  name: 'new-password-field',
  props: ['name'],
  data () {
    return {
      newPassword: '',
      newPasswordAgain: '',
    }
  },
  computed: {
    newPasswordValid () {
      var password = this.newPassword.trim()
      return password.length >= 8
    },
    newPasswordAgainSame () {
      return this.newPassword.trim() == this.newPasswordAgain.trim()
    },
  },
  watch: {
    newPassword: function (val) {
      if (this.newPasswordValid && this.newPasswordAgainSame) {
        this.$emit('value-changed', [this.name, this.newPassword.trim()])
      }
    },
    newPasswordAgain: function (val) {
      if (this.newPasswordValid && this.newPasswordAgainSame) {
        this.$emit('value-changed', [this.name, this.newPassword.trim()])
      }
    },
  },
}
</script>
