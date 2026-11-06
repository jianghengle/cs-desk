<template>
  <div class="container my-page-body">
    <div v-if="token && isAdmin" class="p-3">
      <chat-agent />
    </div>
  </div>
</template>

<script>
import ChatAgent from '../chat-agent/ChatAgent.vue'

export default {
  name: 'AdminChat',
  components: {
    ChatAgent
  },
  data () {
    return {
    }
  },
  computed: {
    token () {
      return this.$store.state.user.token
    },
    isAdmin () {
      return this.$store.state.user.isAdmin
    },
  },
}
</script>
