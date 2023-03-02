<template>
  <v-card
  elevation="2"
  >
    <v-card-title>Available Plugins</v-card-title>
    <v-card-text>
      <v-simple-table>
        <template v-slot:default>
          <thead>
            <tr>
              <th class="text-left">
                Type
              </th>
              <th class="text-left">
                Plugins
              </th>
            </tr>
          </thead>
          <tbody>
            <tr v-for="(type, index) in types_list" v-bind:key="type">
              <td>{{ index }}</td>
              <td>
                <div v-if="types[type]"><v-chip class="ma-2" v-for="t in types[type]['items']" v-bind:key="t">{{ t }}</v-chip></div>
              </td>
            </tr>
          </tbody>
        </template>
      </v-simple-table>
    </v-card-text>
  </v-card>
</template>

<script>
export default {
  name: 'AvailablePlugins',
  data: function () {
      return {
        types: {},
        types_list: {
          "Credentials": "credentials",
          "Scanners": "scanners",
          "Pullers": "pullers",
        }
      }
  },
  mounted() {
    this.fetchTypes(this)
  },
  methods: {
    fetchTypes: (component) => {
      component.$api.get("/types/all").then(
        response => {
          component.types = response.data
      })
    }
  }
}
</script>