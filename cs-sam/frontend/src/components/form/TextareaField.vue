<template>
  <div class="mt-4">
    <div class="field">
      <label class="label">
        <span>{{label}}</span>&nbsp;
        <span class="has-text-danger has-text-weight-light is-size-7" v-if="required">Required</span>
      </label>
      <div class="control">
        <textarea class="textarea" :class="{'my-disbaled-field': readonly}" :placeholder="placeholder" v-model="localValue" :readonly="readonly" :disabled="readonly"></textarea>
      </div>
      <p class="help is-info" v-if="helpInfo">{{helpInfo}}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'textarea-field',
  props: ['name', 'label', 'required', 'value', 'placeholder', 'readonly', 'helpInfo'],
  data () {
    return {
      localValue: null,
    }
  },
  watch: {
    value: function (val) {
      this.setLocalValue()
    },
    localValue: function (val) {
      if (!this.readonly) {
        this.$emit('value-changed', [this.name, this.localValue])
      }
    },
  },
  methods: {
    setLocalValue () {
      if (this.localValue != this.value) {
        this.localValue = String(this.value)
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
