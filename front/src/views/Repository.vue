<template>
  <v-container fluid>
    <v-card>
      <v-card-title  v-if="repository">
        {{ repository.name }}
        <v-spacer></v-spacer>
        <v-btn class="mr-4" color="success" @click="newScanEnabled = true"><v-icon left>mdi-magnify-scan</v-icon>New Scan</v-btn>
      </v-card-title>
      <v-card-subtitle v-if="repository">
        <a :href="repository.url">{{ repository.url }}</a>
        <p><b>Authentication Key : </b><span>{{ authKey }}</span> <v-icon @click="authReveal()">mdi-eye</v-icon> <v-icon @click="authToClipboard()">mdi-clipboard-text</v-icon><HelpToolTip :msg="authKeyHelp" /></p>
      </v-card-subtitle>
      <v-card-text>
        <ScansTable ref="scanList" :repository="repository"/>
      </v-card-text>
    </v-card>
    <NewScanDialog v-if="repository" :cancel="cancelNewScan" :success="confirmNewScan" :enabled="newScanEnabled" :repository="repository"/>
  </v-container>
</template>

<script>
import ScansTable from '@/components/scans/ScansTable'
import HelpToolTip from '@/components/base/HelpToolTip'
import NewScanDialog from '@/components/NewScanDialog'
export default {
  name: 'Repository',
  components: {
    ScansTable,
    HelpToolTip,
    NewScanDialog
  },
  data: function () {
      return {
        repository: undefined,
        authKey: "****",
        uuid: this.$route.params.repoUuid,
        authKeyHelp: "Authentication key is used to authenticate the CLI during a CI scan.",
        newScanEnabled: false
      }
    },
  mounted() {
    this.loadRepositoryInformations();
  },
  methods: {
    cancelNewScan() {
      this.newScanEnabled = false;
    },
    confirmNewScan() {
      this.newScanEnabled = false;
      this.$refs.scanList.loadScans()
    },
    authReveal() {
      this.authKey = this.authKey == '****' ? this.repository.authkey : '****'
    },
    authToClipboard() {
      const clipboardData =
        event.clipboardData ||
        window.clipboardData ||
        event.originalEvent?.clipboardData ||
        navigator.clipboard;

      clipboardData.writeText(this.repository.authkey);
    },
    loadRepositoryInformations() {
      var that = this;
    
      this.$api.get("/repositories/"+this.$route.params.repoUuid).then(
        response => {
          that.repository = response.data
      })
    }
  }
}
</script>
