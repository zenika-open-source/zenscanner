<template>
  <v-container fluid>
    <v-card>
      <v-card-title>
        Secrets
        <v-spacer></v-spacer>
        <v-btn class="mr-4" color="success" @click="dialogNew = true"><v-icon left>mdi-lock</v-icon>New Secret</v-btn>
      </v-card-title>
      <v-card-text>
        <SecretsTable ref="secretList"/>
        <NewSecretDialog :enabled="dialogNew" :cancel="closeNewSecret" :success="successNewSecret"/>
      </v-card-text>
    </v-card>
  </v-container>
</template>

<script>
import SecretsTable from '@/components/SecretsTable'
import NewSecretDialog from '@/components/NewSecretDialog'
export default {
  name: 'Secrets',
  components: {
    SecretsTable,
    NewSecretDialog
  },
  data: function () {
    return {
      dialogNew: false,
    }
  },
  methods: {
    closeNewSecret () {
        this.dialogNew = false;
    },
    successNewSecret() {
      this.dialogNew = false;
      this.$refs.secretList.loadSecrets()
    }
  }
}
</script>
