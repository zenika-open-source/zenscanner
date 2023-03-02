<template>
  <v-container fluid>
    <h2>Dashboard</h2>
    <v-row>
      <v-col><LastScanList /></v-col>
    </v-row>
    <v-row>
      <v-col><AvailablePlugins /></v-col>
      <v-col><Statistics /></v-col>
    </v-row>
  </v-container>
  
</template>

<script>
import AvailablePlugins from '@/components/home/AvailablePlugins'
import LastScanList from '@/components/home/LastScanList'
import Statistics from '@/components/home/Statistics'

export default {
  name: 'Home',

  components: {
    AvailablePlugins,
    LastScanList,
    Statistics
  },
}
</script>
