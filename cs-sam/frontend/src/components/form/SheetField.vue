<template>
  <div class="mt-4">
    <div class="field">
      <label class="label">
        <span>{{label}}</span>&nbsp;
        <span class="has-text-danger has-text-weight-light is-size-7" v-if="required">Required</span>
      </label>
      <div class="control">
        <table class="table table is-fullwidth table is-hoverable">
          <thead>
            <tr>
              <th>#</th>
              <th v-for="(c, i) in columns" :key="'sheet-th-'+name+'-'+i">{{c}}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(r, i) in localValue" :key="'sheet-tr-'+name+'-'+i" :class="{'is-clickable': !readonly}" @click="editRow(i)">
              <th>{{i+1}}</th>
              <td v-for="(c, j) in columns" :key="'sheet-td-'+name+'-'+i+'-'+j">{{r[c]}}</td>
            </tr>
          </tbody>
        </table>
        <a v-if="!readonly" class="button add-row-button" @click="addNewRow">
          <span class="icon">
            <i class="fas fa-plus"></i>
          </span>
          <span>New Row</span>
        </a>
      </div>
      <p class="help is-info" v-if="helpInfo">{{helpInfo}}</p>
    </div>
    <sheet-row-modal :opened="sheetRowModal.opened" :columns="columns" :model="sheetRowModal.model" :index="sheetRowModal.index"
      @sheet-row-modal-closed="onSheetRowModalClosed" @sheet-row-modal-saved="onSheetRowModalSaved" @sheet-row-modal-removed="onSheetRowModalRemoved" />
  </div>
</template>

<script>
import SheetRowModal from '@/components/modals/SheetRowModal'

export default {
  name: 'sheet-field',
  components: {
    SheetRowModal
  },
  props: ['name', 'label', 'required', 'value', 'columns', 'readonly', 'helpInfo'],
  data () {
    return {
      localValue: [],
      sheetRowModal: {
        opened: false,
        index: null,
        model: null,
      }
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
      var valueJson = JSON.stringify(this.value)
      if (valueJson != JSON.stringify(this.localValue)) {
        var value = JSON.parse(valueJson)
        var columns = this.columns
        if (Array.isArray(value)) {
          this.localValue = value.map(i => {
            var row = {}
            for (const c of columns) {
              row[c] = String(i[c])
            }
            return row
          })
        } else {
          this.localValue = []
        }
      }
    },
    addNewRow () {
      this.sheetRowModal.index = null
      var model = {}
      for (const c of this.columns) {
        model[c] = ''
      }
      this.sheetRowModal.model = model
      this.sheetRowModal.opened = true
    },
    editRow (i) {
      if (this.readonly) {
        return
      }
      this.sheetRowModal.index = i
      this.sheetRowModal.model = this.localValue[i]
      this.sheetRowModal.opened = true
    },
    onSheetRowModalClosed () {
      this.sheetRowModal.opened = false
    },
    onSheetRowModalSaved (val) {
      if (this.sheetRowModal.index == null) {
        this.localValue.push(JSON.parse(JSON.stringify(val)))
      } else {
        this.localValue.splice(this.sheetRowModal.index, 1, JSON.parse(JSON.stringify(val)))
      }
      this.sheetRowModal.opened = false
    },
    onSheetRowModalRemoved () {
      this.localValue.splice(this.sheetRowModal.index, 1)
      this.sheetRowModal.opened = false
    },
  },
  mounted () {
    this.setLocalValue()
  },
}
</script>

<style scoped>

.add-row-button {
  margin-top: -15px
}

</style>
