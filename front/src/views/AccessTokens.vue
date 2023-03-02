<template>
  <v-container fluid>
    <v-card>
      <v-card-title>
        My access tokens
        <v-spacer></v-spacer>
        <v-btn class="mr-4" color="success" @click="dialog = true;">
          <v-icon left>mdi-account-key</v-icon>
          New Access Token
        </v-btn>
      </v-card-title>
      <v-card-text>
        <AccessTokensTable ref="ATTable"/>
      </v-card-text>
    </v-card>
    <v-dialog v-model="dialog" max-width="600px">
      <v-card>
        <v-card-title>
          New access token
        </v-card-title>
        <v-card-text>
          <v-container>
            <v-form method="post">
              <v-row>
                <v-text-field label="Access token label" v-model="label" required>
                </v-text-field>
               </v-row>
            </v-form>
          </v-container>
        </v-card-text>
        <v-card-actions>
          <v-spacer></v-spacer>
          <v-btn color="failure" text @click="dialog = false;">
            Cancel
          </v-btn>
          <v-btn color="success" text @click="newAccessToken">
            Submit
          </v-btn>
        </v-card-actions>
      </v-card>
    </v-dialog>
  </v-container>
</template>


<script>
import AccessTokensTable from '@/components/AccessTokensTable.vue'

export default {
  name: 'AccessTokens',
  components: {
    AccessTokensTable,
  },
  data: function () {
    return {
      dialog: false,
      label: undefined,
    }
  },
  methods: {
    newAccessToken () {
      var params = { 'label': this.label }
      var that = this;

      this.$api.post("/access_tokens",
        params)
        .then(
          response => {
            var table = that.$refs.ATTable;
            if (response.status == 200) {
              that.dialog = false;
              table.loadAccessTokens();
              table.snackbar = true;
              table.snackbar_text = "Success !";
            } else {
              table.loadAccessTokens();
              table.snackbar = true;
              table.snackbar_text = "Failure !";
            }
          }
        );
    },
  },
}
</script>
