<template>
  <div class="mt-4">
    <div class="field">
      <label class="label">
        <span>{{label}}</span>&nbsp;
        <span class="has-text-danger has-text-weight-light is-size-7" v-if="required">Required</span>
      </label>

      <div v-if="localValue">
        <div class="control mb-1" v-for="(g, i) in localValue" :key="'strings-field-element-' + i">
          <span class="tag is-medium">
            <span>{{g}}</span>
            <button v-if="!readonly" class="delete ml-3" @click="removeElement(i)"></button>
          </span>
        </div>
      </div>
      <div v-if="!readonly" class="field has-addons">
        <div class="control" v-if="!options">
          <input class="input" type="text" :placeholder="placeholder" v-model="newElement">
        </div>
        <div class="control" v-if="options && !options.allowNew">
          <div class="select" >
            <select v-model="newElement">
              <option  v-for="(opt, i) in allOptions" :key="'strings-field-option-' + i" :value="opt.value">
                {{opt.label}}
              </option>
            </select>
          </div>
        </div>
        <div class="control" v-if="options && options.allowNew">
          <div class="select">
            <select v-model="selectedElement">
              <option  v-for="(opt, i) in allOptions" :key="'strings-field-all-option-' + i" :value="opt.value">
                {{opt.label}}
              </option>
            </select>
          </div>
        </div>
        <div class="control" v-if="selectedElement == '__NEW__'">
          <input class="input" type="text" :placeholder="placeholder" v-model="newElement">
        </div>
        <div class="control">
          <a class="button" @click="addElement">
            <span class="icon is-small">
              <i class="fas fa-plus"></i>
            </span>
          </a>
        </div>
      </div>
      <p class="help is-info my-help-info" v-if="helpInfo">{{helpInfo}}</p>
    </div>
  </div>
</template>

<script>
export default {
  name: 'strings-field',
  props: ['name', 'label', 'required', 'value', 'placeholder', 'readonly', 'options', 'helpInfo'],
  data () {
    return {
      localValue: null,
      newElement: '',
      selectedElement: null,
    }
  },
  computed: {
    allOptions () {
      if (Array.isArray(this.options)) {
        if (this.options.length) {
          var first = this.options[0]
          if (typeof first === 'object') {
            return this.options
          }
          return this.options.map(opt => ({value: opt, label: opt}))
        }
        return []
      }

      var options = []
      if (this.options.values) {
        options = this.options.values.map(function(opt) {
          if (typeof(opt) == 'string') {
            return {label: opt, value: opt}
          }
          return opt
        })
      }
      if (this.options.allowNew) {
        options.push({label: 'New Option', value: '__NEW__'})
      }
      return options
    },
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
      if (this.value) {
        var valueJson = JSON.stringify(this.value)
        if (valueJson != JSON.stringify(this.localValue)) {
          var value = JSON.parse(valueJson)
          if (Array.isArray(value)) {
            this.localValue = value.map(i => String(i))
          } else {
            this.localValue = [String(value)]
          }
        }
      } else {
        this.localValue = []
      }
    },
    removeElement(index) {
      this.localValue.splice(index, 1)
    },
    addElement () {
      this.newElement = this.newElement.trim()
      var newElement = this.newElement
      if (this.selectedElement && this.selectedElement != '__NEW__') {
        newElement = this.selectedElement
      }
      if (!newElement) {
        return
      }
      if (!this.localValue) {
        this.localValue = []
      }
      this.localValue.push(newElement)
      this.newElement = ''
    },
  },
  mounted () {
    this.setLocalValue()
  },
}
</script>

<style scoped>
.my-help-info {
  margin-top: -10px;
}
</style>
