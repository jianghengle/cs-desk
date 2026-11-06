<template>
  <div class="container my-page-body">
    <section class="section">
      <h1 class="title is-5">Home</h1>
      <h2 class="subtitle is-6 mt-2">
        Welcome to your home page!
      </h2>

      <p><router-link :to="'/admin'">Admin page</router-link></p>
    </section>
    
  </div>
</template>

<script>

export default {
  name: 'my-home',
  components: {
  },
  data () {
    return {
      error: '',
      waiting: false,
      
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    token () {
      return this.$store.state.user.token
    },
  },
  methods: {
    
  },
  mounted () {
    
  },
  unmounted () {
    
  },
}
</script>

<style scoped>

</style>
