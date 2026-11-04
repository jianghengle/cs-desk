<template>
  <div>
    <div v-if="error" class="notification is-danger is-light">
      <button class="delete" @click="error=''"></button>
      {{error}}
    </div>

    <div>
      <div class="field has-addons">
        <div class="control">
          <div class="file has-name">
            <label class="file-label">
            <input class="file-input" type="file" @change="onFileChange">
            <span class="file-cta">
                <span class="file-icon">
                  <i class="fas fa-upload"></i>
                </span>
                <span class="file-label">
                  Select File
                </span>
            </span>
            <span class="file-name">
                {{file ? file.name : 'Choose a file...'}}
            </span>
            </label>
          </div>
        </div>
        <div class="control">
          <button class="button" :class="{'is-loading': waiting}" :disabled="!file" @click="upload">
            Upload
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script>
export default {
  name: 'file-upload',
  data () {
    return {
      error: '',
      waiting: false,
      file: null,
    }
  },
  computed: {
    server () {
      return this.$store.state.config.server
    },
  },
  methods: {
    onFileChange (e) {
      var files = e.target.files || e.dataTransfer.files;
      if (!files.length)
        return;
      this.file = files[0];
    },
    upload () {
      if (!this.file || this.waiting) {
        return
      }
      this.waiting = true
      this.error = ''
      this.getS3UploadUrl()
    },
    getS3UploadUrl () {
      var message = {filename: this.file.name}
      this.$http.post(this.server + '/org/get-s3-upload-url', message).then(resp => {
        this.uploadFileToS3(resp.body)
      }, err => {
        this.error = err.body
        this.waiting = false
      })
    },
    uploadFileToS3 (uploadUrl) {
      const axios = require('axios')
      var formData = new FormData();
      Object.keys(uploadUrl.fields).forEach((key) => {
        formData.append(key, uploadUrl.fields[key])
      })
      formData.append('file', this.file)
      var vm = this
      axios.post(uploadUrl.url, formData, {'Content-Type': 'multipart/form-data'}).then(resp => {
        vm.$emit('file-uploaded', {
          filename: uploadUrl.filename,
          bucket: uploadUrl.bucket,
          key: uploadUrl.key
        })
        vm.waiting = false
      }).catch(err => {
        vm.error = err.body
        vm.waiting = false
      })
    },
  },
}
</script>
