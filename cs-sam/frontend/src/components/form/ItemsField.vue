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
              <th v-for="(f, i) in fields" :key="'items-th-'+name+'-'+i" :class="{'has-text-right': f.type=='number'}">{{f.label}}</th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(item, i) in localValue" :key="'items-tr-'+name+'-'+i" :class="{'is-clickable': !readonly}" @click="editItem(i)">
              <th>{{i+1}}</th>
              <td v-for="(f, j) in fields" :key="'items-td-'+name+'-'+i+'-'+j" :class="{'has-text-right': f.type=='number'}">
                <div v-if="f.type == 'strings'">
                  <div v-for="(s, k) in item[f.name]" :key="'items-td-'+name+'-'+i+'-'+j+'-'+k">
                    <span class="tag">
                      {{s}}
                    </span>
                  </div>
                </div>
                <div v-else>
                  <span v-if="f.type=='number' && f.twoDigits">{{Number(item[f.name]).toLocaleString('en-US', {maximumFractionDigits: 2, minimumFractionDigits: 2, useGrouping: false})}}</span>
                  <span v-else>{{item[f.name]}}</span>
                </div>
              </td>
            </tr>
            <tr v-if="sumRow">
              <th>Total</th>
              <th v-for="(f, i) in fields" :key="'items-sr-'+name+'-'+i" :class="{'has-text-right': f.type=='number'}">
                <span v-if="f.type=='number' && f.twoDigits">{{Number(sumRow[f.name]).toLocaleString('en-US', {maximumFractionDigits: 2, minimumFractionDigits: 2, useGrouping: false})}}</span>
                <span v-else>{{sumRow[f.name]}}</span>
              </th>
            </tr>
          </tbody>
        </table>
        <a v-if="!readonly" class="button add-item-button" @click="addNewItem">
          <span class="icon">
            <i class="fas fa-plus"></i>
          </span>
          <span>New Item</span>
        </a>
      </div>
      <p class="help is-info" v-if="helpInfo">{{helpInfo}}</p>
    </div>

    <items-item-modal :opened="itemsItemModal.opened" :fields="fields" :model="itemsItemModal.model" :index="itemsItemModal.index" :parentModel="parentModel"
      @items-item-modal-closed="onItemsItemModalClosed" @items-item-modal-saved="onItemsItemModalSaved" @items-item-modal-removed="onItemsItemModalRemoved" />

  </div>
</template>

<script>
import ItemsItemModal from '@/components/modals/ItemsItemModal'

export default {
  name: 'items-field',
  components: {
    ItemsItemModal
  },
  props: ['name', 'label', 'required', 'value', 'fields', 'readonly', 'parentModel', 'helpInfo'],
  data () {
    return {
      localValue: [],
      itemsItemModal: {
        opened: false,
        index: null,
        model: null,
      }
    }
  },
  computed: {
    sumRow () {
      var row = {}
      for (const f of this.fields) {
        if (f.type == 'number' && f.showSum) {
          var sum = 0
          for (const item of this.localValue) {
            sum = sum + Number(item[f.name])
          }
          row[f.name] = sum
        }
      }
      if (Object.keys(row).length) {
        return row
      }
      return null
    },
  },
  watch: {
    value: function (val) {
      this.setLocalValue()
    },
    localValue: function (val) {
      if (!this.readonly) {
        this.$emit('value-changed', [this.name, JSON.parse(JSON.stringify(this.localValue))])
      }
    },
  },
  methods: {
    setLocalValue () {
      var valueJson = JSON.stringify(this.value)
      if (valueJson != JSON.stringify(this.localValue)) {
        var value = JSON.parse(valueJson)
        var fields = this.fields
        if (Array.isArray(value)) {
          this.localValue = value.map(i => {
            var item = {}
            for (const f of fields) {
              if (f.type == 'string') {
                item[f.name] = String(i[f.name])
              } else if (f.type == 'number') {
                item[f.name] = Number(i[f.name])
              } else if (f.type == 'strings') {
                item[f.name] = i[f.name]
              }
            }
            return item
          })
        } else {
          this.localValue = []
        }
      }
    },
    addNewItem () {
      this.itemsItemModal.index = null
      var model = {}
      for (const f of this.fields) {
        if (f.type == 'string') {
          model[f.name] = ''
        } else if (f.type == 'number') {
          model[f.name] = ''
        } else if (f.type == 'strings') {
          model[f.name] = []
        }
      }
      this.itemsItemModal.model = model
      this.itemsItemModal.opened = true
    },
    editItem (i) {
      if (this.readonly) {
        return
      }
      this.itemsItemModal.index = i
      this.itemsItemModal.model = this.localValue[i]
      this.itemsItemModal.opened = true
    },
    onItemsItemModalClosed () {
      this.itemsItemModal.opened = false
    },
    onItemsItemModalSaved (val) {
      if (this.itemsItemModal.index == null) {
        this.localValue.push(JSON.parse(JSON.stringify(val)))
      } else {
        this.localValue.splice(this.itemsItemModal.index, 1, JSON.parse(JSON.stringify(val)))
      }
      this.itemsItemModal.opened = false
    },
    onItemsItemModalRemoved () {
      this.localValue.splice(this.itemsItemModal.index, 1)
      this.itemsItemModal.opened = false
    },
  },
  mounted () {
    this.setLocalValue()
  },
}
</script>

<style scoped>

.add-item-button {
  margin-top: -15px
}

</style>
