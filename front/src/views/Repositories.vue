<template>
  <v-container fluid>
    <v-card>
      <v-card-title>
        My Repositories
        <v-spacer></v-spacer>
        <v-btn class="mr-4" color="success" @click="$router.push('/repositories/new')"><v-icon left>mdi-folder</v-icon>New Repository</v-btn>
      </v-card-title>
      <v-card-text>
        <RepositoriesTable/>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import RepositoriesTable from '@/components/RepositoriesTable.vue'
export default {
  name: 'Repositories',
  components: {
    RepositoriesTable
  }
}
</script>
