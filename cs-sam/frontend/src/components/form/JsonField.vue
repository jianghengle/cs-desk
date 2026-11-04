<template>
  <div class="mt-4">
    <div class="field">
      <label class="label">
        <span>{{label}}</span>&nbsp;
        <span class="has-text-danger has-text-weight-light is-size-7" v-if="required">Required</span>
      </label>
      <div class="control">
        <textarea class="textarea" :class="{'my-disbaled-field': readonly, 'is-danger': !isValidJson}" :placeholder="placeholder" v-model="localValue" :readonly="readonly" :disabled="readonly"></textarea>
      </div>
      <p class="help is-danger" v-if="!isValidJson">Invalid JSON.</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'json-field',
  props: ['name', 'label', 'required', 'value', 'placeholder', 'readonly'],
  data () {
    return {
      localValue: null,
    }
  },
  computed: {
    isValidJson () {
      if (typeof this.localValue != 'string') {
          return false
      }
      var value = null
      try {
        value = JSON.parse(this.localValue)
      } catch (error) {
        return false
      }
      return true
    },
  },
  watch: {
    value: function (val) {
      this.setLocalValue()
    },
    localValue: function (val) {
      if (!this.readonly && this.isValidJson) {
        this.$emit('value-changed', [this.name, JSON.parse(this.localValue)])
      }
    },
  },
  methods: {
    setLocalValue () {
      if (this.localValue != JSON.stringify(this.value)) {
        this.localValue = JSON.stringify(this.value)
      }
    },
  },
  mounted () {
    this.setLocalValue()
  },
}
</script>

<style scoped>

</style>>
