<template>
  <div class="mt-4">
    <div class="field">
      <label class="label">
        <span>{{label}}</span>&nbsp;
        <span class="has-text-danger has-text-weight-light is-size-7" v-if="required">Required</span>
      </label>
      <div class="control">
        <label class="checkbox" :disabled="readonly">
          <input type="checkbox" v-model="localValue" :disabled="readonly">
          {{inlineLabel}}
        </label>
      </div>
      <p class="help is-info" v-if="helpInfo">{{helpInfo}}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'checkbox-field',
  props: ['name', 'label', 'required', 'value', 'inlineLabel', 'readonly', 'helpInfo'],
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
        this.localValue = Boolean(this.value)
      }
    },
  },
  mounted () {
    this.setLocalValue()
  },
}
</script>
