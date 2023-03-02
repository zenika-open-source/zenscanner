<template>
  <v-container fluid>
    <v-card>
      <v-card-title>
        Vulnerabilities
      </v-card-title>
      <v-card-text>
        <VulnerabiliesTable />
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import VulnerabiliesTable from '@/components/VulnerabiliesTable'
export default {
  name: 'Vulnerabilities',
  components: {
    VulnerabiliesTable
  },
  data: function () {
    return {}
  },
  methods: {
  }
}
</script>
