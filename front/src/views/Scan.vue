<template>
  <v-container fluid>
    <v-card>
      <v-card-title  v-if="scan">
        Scan details for {{ scan.repository.name }} ({{ scan.branch }})
        <v-spacer></v-spacer>
        <v-btn class="mr-4" color="primary" @click="openCode()"><v-icon left>mdi-code-tags</v-icon>View Code</v-btn>
        <v-btn class="mr-4" color="primary" @click="$router.push({ name: 'repository', params: { repoUuid: scan.repository.uuid }})"><v-icon left>mdi-folder</v-icon>View Repository</v-btn>
      </v-card-title>
      <v-card-subtitle>
       </v-card-subtitle>
      <v-card-text>
        <VulnerabiliesTable v-if="scan" :scanUUID="uuid" :scan="scan"/>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import VulnerabiliesTable from '@/components/VulnerabiliesTable'
export default {
  name: 'Scan',
  components: {
    VulnerabiliesTable
  },
  data: function () {
      return {
        uuid: this.$route.params.scanUuid,
        scan: undefined
      }
    },
  mounted() {
    this.loadScanInformations();
  },
  methods: {
    openCode() {
      window.open(this.scan.commit_url, '_blank')
    },
    loadScanInformations() {
      var that = this;
    
      this.$api.get("/scans/"+this.uuid).then(
        response => {
          that.scan = response.data
      })
    }
  }
}
</script>
