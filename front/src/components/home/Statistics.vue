<template>
  <v-card
  elevation="2"
  >
    <v-card-title>Statistics</v-card-title>
    <v-card-text>
      <v-simple-table>
        <template v-slot:default>
          <thead>
            <tr>
              <th class="text-left">
                Type
              </th>
              <th class="text-left">
                Count
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>Repositories</td>
              <td>{{ total_repositories }}</td>
            </tr>
            <tr>
              <td>Scans</td>
              <td>{{ total_scans }}</td>
            </tr>
            <tr>
              <td>Vulnerabilites</td>
              <td>{{ total_vulnerabilities }}</td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </v-card-text>
    <v-card-title>Vulnerabilities By Level</v-card-title>
    <v-card-text>
      <v-simple-table>
        <template v-slot:default>
          <thead>
            <tr>
              <th class="text-left">
                <v-chip class="ma-2" color="red" label text-color="black">HIGH</v-chip>
              </th>
              <th class="text-left">
                <v-chip class="ma-2" color="orange" label text-color="black">MEDIUM</v-chip>
              </th>
              <th class="text-left">
                <v-chip class="ma-2" color="yellow" label text-color="black">LOW</v-chip>
              </th>
            </tr>
          </thead>
          <tbody>
            <tr>
              <td>{{ total_high_vulnerabilities }}</td>
              <td>{{ total_medium_vulnerabilities }}</td>
              <td>{{ total_low_vulnerabilities }}</td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'Statistics',
  data: function () {
      return {
        total_repositories: 0,
        total_scans: 0,
        total_vulnerabilities: 0,
        total_high_vulnerabilities: 0,
        total_medium_vulnerabilities: 0,
        total_low_vulnerabilities: 0,
      }
  },
  mounted() {
    this.fetchRepositories(this)
    this.fetchVulnerabilies(this)
    this.fetchHighVulnerabilies(this)
    this.fetchMediumVulnerabilies(this)
    this.fetchLowVulnerabilies(this)
    this.fetchScans(this)
  },
  methods: {
    fetchRepositories: (component) => {
      component.$api.get("/repositories?limit=1").then(
        response => {
          component.total_repositories = response.data['count']
      })
    },
    fetchVulnerabilies: (component) => {
      component.$api.get("/vulnerabilities?limit=1&new=1").then(
        response => {
          component.total_vulnerabilities = response.data['count']
      })
    },
    fetchHighVulnerabilies: (component) => {
      component.$api.get("/vulnerabilities?limit=1&new=1&level=3").then(
        response => {
          component.total_high_vulnerabilities = response.data['count']
      })
    },
    fetchMediumVulnerabilies: (component) => {
      component.$api.get("/vulnerabilities?limit=1&new=1&level=2").then(
        response => {
          component.total_medium_vulnerabilities = response.data['count']
      })
    },
    fetchLowVulnerabilies: (component) => {
      component.$api.get("/vulnerabilities?limit=1&new=1&level=1").then(
        response => {
          component.total_low_vulnerabilities = response.data['count']
      })
    },
    fetchScans: (component) => {
      component.$api.get("/scans?limit=1").then(
        response => {
          component.total_scans = response.data['count']
      })
    }
  }
}
</script>