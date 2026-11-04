<template>
  <div class="container my-page-body">
    <div v-if="token" class="p-3">
      <nav class="breadcrumb" aria-label="breadcrumbs">
        <ul>
          <li>
            <router-link :to="'/admin'" aria-current="page">Tables</router-link>
          </li>
          <li>
            <router-link :to="'/admin/table/' + tableModel" aria-current="page">{{ table ? table.tableName : tableModel }}</router-link>
          </li>
          <li class="is-active">
            <a href="#" aria-current="page">{{ itemId }}</a>
          </li>
        </ul>
      </nav>

      <div v-if="waitingTable">
        <span class="icon is-medium is-size-4">
          <i class="fas fa-spinner fa-pulse"></i>
        </span>
      </div>
      <div v-else>
        <h1 class="title is-5">{{table && table.tableName}}&nbsp;item</h1>

        <div v-if="waitingItem">
          <span class="icon is-medium is-size-4">
            <i class="fas fa-spinner fa-pulse"></i>
          </span>
        </div>
        <div v-else>
          <div v-for="(f, i) in fields" :key="'field-'+i">
            <div v-if="isNew">
              <div v-if="f.type == 'bool' && !f.modifiers.includes('auto')">
                <checkbox-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  @value-changed="onValueChanged" />
              </div>
              <div v-if="(f.type == 'int' || f.type == 'float') && !f.modifiers.includes('auto')">
                <number-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'timestamp' && !f.modifiers.includes('auto')">
                <number-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'enum' && !f.modifiers.includes('auto')">
                <string-field :name="f.name" :label="f.name" :value="localItem[f.name]" :options="f.modifiers[0]"
                  @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'str' && !f.modifiers.includes('auto')">
                <string-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  :required="f.modifiers.includes('required')" @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'text' && !f.modifiers.includes('auto')">
                <textarea-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  :readonly="f.modifiers.includes('readonly') || f.modifiers.includes('auto')"
                  @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'list' && !f.modifiers.includes('auto')">
                <strings-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'obj' && !f.modifiers.includes('auto')">
                <json-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'email' && !f.modifiers.includes('auto')">
                <string-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  :constraints="emailConstraints" @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'password' && !f.modifiers.includes('auto')">
                <new-password-field :name="'password'" @value-changed="onValueChanged" />
              </div>
            </div>
            <div v-else>
              <div v-if="f.type == 'bool'">
                <checkbox-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  :readonly="f.modifiers.includes('readonly') || f.modifiers.includes('auto')"
                  @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'int' || f.type == 'float'">
                <number-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  :readonly="f.modifiers.includes('readonly') || f.modifiers.includes('auto')"
                  @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'timestamp'">
                <div v-if="f.modifiers.includes('readonly') || f.modifiers.includes('auto')">
                  <string-field :name="f.name" :label="f.name" :readonly="true"
                    :value="timestampToDatetime(localItem[f.name])" />
                </div>
                <div v-else>
                  <number-field :name="f.name" :label="f.name"
                    :value="localItem[f.name]" @value-changed="onValueChanged" />
                </div>
              </div>
              <div v-if="f.type == 'enum'">
                <string-field :name="f.name" :label="f.name" :value="localItem[f.name]" :options="f.modifiers[0]"
                  :readonly="f.modifiers.includes('readonly') || f.modifiers.includes('auto')"
                  @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'str'">
                <string-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  :readonly="f.modifiers.includes('readonly') || f.modifiers.includes('auto')"
                  :required="f.modifiers.includes('required')" @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'text'">
                <textarea-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  :readonly="f.modifiers.includes('readonly') || f.modifiers.includes('auto')"
                  @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'list'">
                <strings-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  :readonly="f.modifiers.includes('readonly') || f.modifiers.includes('auto')"
                  @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'obj'">
                <json-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  :readonly="f.modifiers.includes('readonly') || f.modifiers.includes('auto')"
                  @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'email'">
                <string-field :name="f.name" :label="f.name" :value="localItem[f.name]"
                  :readonly="f.modifiers.includes('readonly') || f.modifiers.includes('auto')"
                  :constraints="emailConstraints" @value-changed="onValueChanged" />
              </div>
              <div v-if="f.type == 'password' && !f.modifiers.includes('readonly') && !f.modifiers.includes('auto')">
                <div class="mt-4">
                  <div class="field">
                    <label class="label">
                      <span>Password</span>
                    </label>
                    <div class="field">
                      <div class="control">
                        <button class="button" @click="changePasswordModal.opened = true">Change password</button>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <div v-if="isNew">
            <div class="field is-grouped mt-6">
              <div class="control">
                <button class="button is-link" :disabled="!itemValid" :class="{'is-loading': waitingCreate}" @click="createItem">
                  <i class="fas fa-save"></i>&nbsp;&nbsp;
                  <span>Save</span>
                </button>
              </div>
            </div>
          </div>
          <div v-else class="field is-grouped mt-6">
            <div class="control">
              <button class="button is-link" :disabled="!changes.length || !itemValid" :class="{'is-loading': waitingUpdate}" @click="updateItem">
                <i class="fas fa-save"></i>&nbsp;&nbsp;
                <span>Save</span>
              </button>
            </div>
            <div class="control">
              <button class="button" :disabled="!changes.length" @click="resetItem">Reset</button>
            </div>
            <div class="control">
              <button class="button is-danger is-outlined" :disabled="Boolean(changes.length)" @click="deleteItem">
                <span class="icon">
                  <i class="far fa-trash-alt"></i>
                </span>
                <span>Delete</span>
              </button>
            </div>
          </div>

          <article class="message is-warning mt-5" v-if="changes.length && !isNew">
            <div class="message-body">
              You have unsaved changes.
            </div>
          </article>

          <article class="message is-success mt-5" v-if="createSucceeded">
            <div class="message-body">
              Created item successfully.
            </div>
          </article>

          <article class="message is-success mt-5" v-if="updateSucceeded">
            <div class="message-body">
              Updated item successfully.
            </div>
          </article>

          <article class="message is-success mt-5" v-if="deleteSucceeded">
            <div class="message-body">
              Deleted item successfully.
            </div>
          </article>

          <change-password-modal :opened="changePasswordModal.opened" @closeChangePasswordModal="changePasswordModal.opened = false" />
        </div>
      </div>
    </div>
  </div>
</template>

<script>
import dateFormat from 'dateformat'
import StringField from '../components/form/StringField.vue'
import StringsField from '../components/form/StringsField.vue'
import NumberField from '../components/form/NumberField.vue'
import JsonField from '../components/form/JsonField.vue'
import TextareaField from '../components/form/TextareaField.vue'
import CheckboxField from '../components/form/CheckboxField.vue'
import ChangePasswordModal from '../components/modals/ChangePasswordModal.vue'
import NewPasswordField from '../components/form/NewPasswordField.vue'

export default {
  name: 'admin-table-item',
  components: {
    StringField,
    StringsField,
    CheckboxField,
    NumberField,
    JsonField,
    TextareaField,
    ChangePasswordModal,
    NewPasswordField,
  },
  data () {
    return {
      error: '',
      waitingTable: false,
      waitingItem: false,
      waitingUpdate: false,
      waitingCreate: false,
      waitingDelete: false,
      table: null,
      item: null,
      localItem: null,
      createSucceeded: false,
      deleteSucceeded: false,
      updateSucceeded: false,
      changePasswordModal: {
        opened: false,
      },
      emailConstraints: [{
        match: /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/
      }]
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
    adminPrefix () {
      return this.$store.state.config.adminPrefix
    },
    token () {
      return this.$store.state.user.token
    },
    tableModel () {
      return this.$route.params.tableModel
    },
    itemId () {
      return this.$route.params.itemId
    },
    isNew () {
      return this.itemId == 'new'
    },
    fields () {
      if (!this.table) {
        return []
      }
      var tableFields = this.table.fields
      if (this.isNew) {
        tableFields = tableFields.slice(1)
      }
      var fields = []
      for (var f of tableFields) {
        if (f[2] && f[2] == 'hidden') {
          continue
        }
        var name = f[0]
        var type = f[1] || 'obj'
        var modifiers = f.slice(2)
        fields.push({name: name, type: type, modifiers})
      }
      return fields
    },
    changes () {
      var changes = []
      for (var f of this.fields) {
        if (f.modifiers.includes('readonly') || f.modifiers.includes('hidden') || f.modifiers.includes('auto')) {
          continue
        }
        if (JSON.stringify(this.item[f.name]) != JSON.stringify(this.localItem[f.name])) {
          changes.push({name: f.name, value: this.localItem[f.name]})
        }
      }
      if (changes.length) {
        this.updateSucceeded = false
      }
      return changes
    },
    itemValid () {
      for (var f of this.fields) {
        if (this.isNew && f.type == 'password' && !this.localItem.password) {
          return false
        }
        if (f.type == 'email' && !this.localItem[f.name]) {
          return false
        }
        if (f.type == 'str' && f.modifiers.includes('required') && !this.localItem[f.name]) {
          return false
        }
      }
      return true
    },
  },
  watch: {
    itemId: function (val) {
      this.createSucceeded = false
      this.updateSucceeded = false
      this.getTable()
    },
  },
  methods: {
    getTable () {
      this.waitingTable = true
      this.$http.get(this.server + this.adminPrefix + 'get-table/' + this.tableModel).then(resp => {
        this.table = resp.body
        this.waitingTable = false
        if (this.isNew) {
          this.item = {}
          var localItem  = {}
          for (var f of this.fields) {
            if (f.type == 'email') {
              localItem[f.name] = ''
            } else if (f.type == 'password') {
              localItem.password = ''
            } else if (f.modifiers.includes('required')) {
              localItem[f.name] = null
            }
          }
          this.localItem = localItem
        } else {
          this.getItem()
        }
      }, err => {
        this.error = err.body
        this.waitingTable = false
      })
    },
    getItem () {
      this.waitingItem = true
      this.$http.get(this.server + this.adminPrefix + this.tableModel + '/get-item/' + this.itemId).then(resp => {
        this.item = resp.body
        this.localItem = JSON.parse(JSON.stringify(resp.body))
        this.waitingItem = false
      }, err => {
        this.error = err.body
        this.waitingItem = false
      })
    },
    timestampToDatetime (t) {
      if (!t) {
        return ''
      }
      var dt = new Date(t * 1000)
      var format = 'yyyy-mm-dd HH:MM:ss'
      return dateFormat(dt, format)
    },
    onValueChanged (val) {
      var name = val[0]
      var value = JSON.parse(JSON.stringify(val[1]))
      if (typeof value === "string") {
        value = value.trim()
      }
      this.localItem[name] = value
    },
    createItem () {
      if (!this.itemValid) {
        return
      }
      this.waitingCreate = true
      var message = {...this.localItem}
      this.$http.post(this.server + this.adminPrefix + this.tableModel + '/create-item', message).then(resp => {
        var item = resp.body
        var itemId = item[this.table.fields[0][0]]
        this.waitingCreate = false
        this.createSucceeded = true
        var vm = this
        setTimeout(() => {
          vm.$router.replace('/admin/item/' + vm.tableModel + '/' + itemId)
        }, 1000)
      }, err => {
        this.error = err.body
        this.waitingSucceeded = false
      })
    },
    updateItem () {
      if (!this.changes.length) {
        return
      }
      this.waitingUpdate = true
      var message = {}
      for (var c of this.changes) {
        message[c.name] = c.value
      }
      this.$http.post(this.server + this.adminPrefix + this.tableModel + '/update-item/' + this.itemId, message).then(resp => {
        this.item = resp.body
        this.localItem = JSON.parse(JSON.stringify(resp.body))
        this.waitingUpdate = false
        this.updateSucceeded = true
      }, err => {
        this.error = err.body
        this.waitingUpdate = false
      })
    },
    resetItem () {
      if (this.changes.length) {
        this.localItem = JSON.parse(JSON.stringify(this.item))
      }
    },
    deleteItem () {
      if (this.changes.length) {
        return
      }
      var confirm = {
        title: 'Delete item',
        message: 'Are you sure to delete this item ' + this.itemId + '?',
        button: 'Yes, I am sure.',
        callback: {
          context: this,
          method: this.deleteItemConfirmed,
          args: []
        }
      }
      this.$store.commit('modals/openConfirmModal', confirm)
    },
    deleteItemConfirmed () {
      this.waitingDelete = true
      var message = {}
      this.$http.post(this.server + this.adminPrefix + this.tableModel + '/delete-item/' + this.itemId, message).then(resp => {
        this.waitingDelete = false
        this.deleteSucceeded = true
        var vm = this
        setTimeout(() => {
          vm.$router.replace('/admin/table/' + vm.tableModel)
        }, 1000)
      }, err => {
        this.error = err.body
        this.waitingDelete = false
      })
    },
    closeChangePasswordModal () {
      this.changePasswordModal.opened = false
    },
  },
  mounted () {
    this.$nextTick(() => {
      if (this.token) {
        this.getTable()
      } else {
        this.$router.replace('/admin')
      }
    })
  },
}
</script>

<style scoped>

</style>
