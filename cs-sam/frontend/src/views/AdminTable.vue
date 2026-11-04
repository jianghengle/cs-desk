<template>
  <div class="container my-page-body">
    <div v-if="token" class="p-3">
      <nav class="breadcrumb" aria-label="breadcrumbs">
        <ul>
          <li>
            <router-link :to="'/admin'" aria-current="page">Tables</router-link>
          </li>
          <li class="is-active">
            <a href="#" aria-current="page">{{ table ? table.tableName : tableModel }}</a>
          </li>
        </ul>
      </nav>

      <div v-if="waitingTable">
        <span class="icon is-medium is-size-4">
          <i class="fas fa-spinner fa-pulse"></i>
        </span>
      </div>
      <div v-else>
        <div>
          <div class="buttons is-pulled-right">
            <router-link class="button" :to="'/admin/item/' + tableModel + '/new'">
              <span class="icon is-small">
                <i class="fas fa-plus"></i>
              </span>
              <span>New</span>
            </router-link>
          </div>
          <h1 class="title is-5">
            <span>{{table && table.tableName}}</span>&nbsp;
            <span class="is-size-6 has-text-weight-normal">Total items: ~{{ table && table.metadata.itemCount }}</span>
          </h1>
          <div class="field has-addons" v-if="selectedQuery">
            <p class="control">
              <span class="select">
                <select v-model="queryMode">
                  <option v-for="(opt, i) in queryModes" :key="'query-opt-' + i">{{opt}}</option>
                </select>
              </span>
            </p>
            <p class="control" v-for="(qm, i) in queryModes" :key="'qm-'+i" v-if="qm != 'Scan' && queries[qm]">
              <input class="input" type="text" :placeholder="selectedQuery.indexField" v-show="selectedQuery.mode == qm" v-model="queries[qm].indexValue">
            </p>
            <p class="control">
              <button class="button" @click="reQuery">
                {{ selectedQuery.mode == 'Scan' ? 'Scan' : 'Query' }}
              </button>
            </p>
          </div>
        </div>

        <div class="my-overflow mt-3">
          <table class="table is-fullwidth is-hoverable">
            <thead>
              <tr>
                <th>#</th>
                <th v-for="(f, i) in displayFields" :key="'th-'+i" :class="{'has-text-right': f.type == 'num'}"
                  class="is-clickable" @click="changeSort(f.name)">
                  <span>{{ f.name }}</span>
                  <span class="icon" v-if="selectedQuery.sortBy == f.name">
                    <i class="fas" :class="{'fa-sort-up': selectedQuery.asc, 'fa-sort-down': !selectedQuery.asc}"></i>
                  </span>
                </th>
              </tr>
            </thead>
            <tbody>
              <tr v-for="(item, i) in displayItems" :key="'tr-'+i">
                <td>{{ i + 1 }}</td>
                <td v-for="(f, j) in displayFields" :key="'td-'+i+'-'+j" :class="{'has-text-right': f.type == 'num'}">
                  <span v-if="f.type == 'timestamp'">
                    {{ timestampToDatetime(item[f.name]) }}
                  </span>
                  <span v-else>
                    <router-link v-if="j==0" :to="'/admin/item/' + tableModel + '/' + item[f.name]">
                      {{ item[f.name] }}
                    </router-link>
                    <span v-else>
                      {{ item[f.name] }}
                    </span>
                  </span>
                </td>
              </tr>
            </tbody>
          </table>
        </div>

        <div v-if="waitingItems">
          <span class="icon is-medium is-size-4">
            <i class="fas fa-spinner fa-pulse"></i>
          </span>
        </div>

        <div class="buttons mt-3" v-if="selectedQuery">
          <button class="button" :disabled="!selectedQuery.hasMore" @click="runQuery">
            <span class="icon is-small" v-if="selectedQuery.hasMore">
              <i class="fas fa-chevron-down"></i>
            </span>
            <span>{{ selectedQuery.hasMore ? 'Continue' : 'The end' }}</span>
          </button>
        </div>
      </div>
    </div>
    
  </div>
</template>

<script>
import dateFormat from 'dateformat'

export default {
  name: 'admin-table',
  components: {
  },
  data () {
    return {
      error: '',
      waitingTable: false,
      waitingItems: false,
      table: null,
      queryMode: 'Scan',
      queryModes: [],
      queries: {},
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
    displayFields () {
      if (!this.table) {
        return []
      }
      var fields = []
      for (var f of this.table.fields) {
        if (f[2] && f[2] == 'hidden') {
          continue
        }
        if (f[1] == 'str' || f[1] == 'email' || f[1] == 'enum' || f[1] == 'bool' || f[1] == 'timestamp') {
          fields.push({name: f[0], type: f[1]})
        } else if (f[1] == 'int' || f[1] == 'float') {
          fields.push({name: f[0], type: 'num'})
        }
      }
      return fields
    },
    selectedQuery () {
      return this.queries[this.queryMode]
    },
    displayItems () {
      if (!this.selectedQuery) {
        return []
      }
      var items = this.selectedQuery.items.slice()
      if (!this.selectedQuery.sortBy) {
        return items
      }
      var sortBy = this.selectedQuery.sortBy
      var sortByField = this.displayFields.find(f => f.name == sortBy)
      var asc = this.selectedQuery.asc
      items.sort((a, b) => {
        var va = a[sortBy]
        var vb = b[sortBy]
        if (sortByField.type == 'num' || sortByField.type == 'timestamp') {
          return asc ? va - vb : vb - va
        }
        va = String(va)
        vb = String(vb)
        return asc ? va.localeCompare(vb) : vb.localeCompare(va)
      })
      return items
    },
  },
  watch: {
    tableModel: function (val) {
      if (val) {
        this.getTable()
      }
    },
  },
  methods: {
    getTable () {
      this.waitingTable = true
      this.$http.get(this.server + this.adminPrefix + 'get-table/' + this.tableModel).then(resp => {
        this.table = resp.body
        this.initQueries()
        this.waitingTable = false
      }, err => {
        this.error = err.body
        this.waitingTable = false
      })
    },
    initQueries () {
      var queryModes = ['Scan']
      var queries = {
        Scan: {
          mode: 'Scan',
          limit: 100,
          lastKey: null,
          hasMore: true,
          items: [],
          sortBy: null,
          asc: true,
        }
      }
      if (this.table.indexes) {
        for (var indexName in this.table.indexes) {
          var indexField = this.table.indexes[indexName]
          var mode = 'Query by ' + indexField
          queryModes.push(mode)
          queries[mode] = {
            mode: mode,
            indexName: indexName,
            indexField: indexField,
            indexValue: '',
            limit: 100,
            lastKey: null,
            hasMore: true,
            items: [],
            sortBy: null,
            asc: true,
          }
        }
      }
      this.queryModes = queryModes
      this.queries = queries
      this.scanTable()
    },
    reQuery () {
      var query = this.queries[this.queryMode]
      query.items = []
      query.lastKey = null
      query.hasMore = true
      this.runQuery()
    },
    runQuery () {
      if (!this.selectedQuery.hasMore) {
        return
      }
      if (this.selectedQuery.mode == 'Scan') {
        this.scanTable()
      } else {
        this.queryTable()
      }
    },
    scanTable () {
      this.waitingItems = true
      var scan = this.selectedQuery
      var message = {
        limit: scan.limit,
        startKey: scan.lastKey,
      }
      this.$http.post(this.server + this.adminPrefix + this.tableModel + '/scan-items', message).then(resp => {
        var result = resp.body
        scan.items = scan.items.concat(result.items)
        scan.lastKey = result.lastKey
        if (!result.lastKey) {
          scan.hasMore = false
        }
        this.waitingItems = false
      }, err => {
        this.error = err.body
        this.waitingItems = false
      })
    },
    queryTable () {
      this.waitingItems = true
      var query = this.selectedQuery
      var message = {
        indexName: query.indexName,
        indexValue: query.indexValue,
        limit: query.limit,
        startKey: query.lastKey,
      }
      this.$http.post(this.server + this.adminPrefix + this.tableModel + '/query-items', message).then(resp => {
        var result = resp.body
        query.items = query.items.concat(result.items)
        query.lastKey = result.lastKey
        if (!result.lastKey) {
          query.hasMore = false
        }
        this.waitingItems = false
      }, err => {
        this.error = err.body
        this.waitingItems = false
      })
    },
    timestampToDatetime (t) {
      var dt = new Date(t * 1000)
      var format = 'yyyy-mm-dd HH:MM'
      return dateFormat(dt, format)
    },
    changeSort (fieldName) {
      var query = this.queries[this.queryMode]
      if (query.sortBy == fieldName) {
        query.asc = !query.asc
      } else {
        query.sortBy = fieldName
      }
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
.my-overflow {
  overflow-x: scroll;
}
</style>
