<template>
  <div>

    <v-data-table 
      :headers="headers"
      :items="access_tokens"
      :items-per-page="10"
      :options.sync="options"
      :server-items-length="totalAts"
      :loading="loading"
      loading-text="Loading... Please wait"
      >

      <template v-slot:top>
        <v-container fluid>
        <v-row>
          <v-col>
            <v-text-field
              v-model="search.label"
              label="Label"
              append-icon="mdi-magnify"
            ></v-text-field>
          </v-col>
          <v-col>
            <v-text-field
              v-model="search.token"
              label="Token"
              append-icon="mdi-magnify"
            ></v-text-field>
          </v-col>
        </v-row>
        </v-container>
      </template>

      <template v-slot:item="row">
        <tr>
          <td>{{row.item.label}}</td>
          <td>{{row.item.token}}</td>
          <td>
            <ToolTipAction msg="Copy token" icon="content-copy" :args="row.item.token" :callback="copyValue" />
            <ToolTipAction msg="Delete token" icon="delete" :args="row.item.token" :callback="openDeleteDialog" />
          </td>
        </tr>
      </template>
    </v-data-table>
    <DeleteDialog text="Are you sure?" title="Delete ?" :confirm="deleteAT" :close="cancelDelete" :enabled="dialog"/>
    <v-snackbar  v-model="snackbar" timeout="3000">{{ snackbar_text }}</v-snackbar>
  </div>
</template>

<script>
import DeleteDialog from '@/components/base/DeleteDialog'
import ToolTipAction from '@/components/base/ToolTipAction'

export default {
  name: 'AccessTokensTable',
  components: {
    DeleteDialog,
    ToolTipAction,
  },
  data: function() {
    return {
      loading: false,
      access_tokens: [],
      todelete: null,
      totalAts: 0,
      options: {},
      dialog: false,
      snackbar: false,
      snackbar_text: null,
      search: {
        "label": "",
        "token": ""
      },
      headers: [
        {text: 'Name', value: 'label'},
        {text: 'Value', value: 'token'},
        {text: 'Actions', value: ''},
      ],
    }
  },
  watch: {
    options: {
      handler () {
        this.loadAccessTokens()
      },
      deep: true,
    },
    search: {
      handler () {
        this.options['page'] = 1;
        this.loadAccessTokens();
      },
      deep: true,
    }
  },
  mounted() {
    this.loadAccessTokens();
  },
  methods: {
    openDeleteDialog(item) {
      this.todelete = item;
      this.dialog = true;
    },
    cancelDelete() {
      this.dialog=false;
      this.todelete=null;
    },
    copyValue(v) {
      navigator.clipboard.writeText(v);
    },
    deleteAT() {
      var that = this;
      this.$api.delete("/access_tokens/"+this.todelete)
        .then(
          response => {
            if (response.status == 200) {
              that.snackbar_text = "Success !";
              that.snackbar = true;
              that.loadAccessTokens();
            } else {
              that.snackbar_text = "Failed !";
              that.snackbar = true;
            }
          }
        );
      this.dialog = false;
      this.todelete = null;
    },
    loadAccessTokens() {
      var that = this;
      this.loading = true;
      let params = {
        'limit': that.options['itemsPerPage'],
        'offset': that.options['itemsPerPage']*(that.options['page']-1),
      }

      if (this.search.label != "") {
        params['label'] = this.search.label;
      }
      if (this.search.token != "") {
        params['token'] = this.search.token;
      }

      if (this.options.sortBy.length > 0) {
        params['order_by'] = this.options.sortBy[0];
        if (this.options.sortDesc[0]) {
          params['ascending'] = 1
        } else {
          params['ascending'] = 0
        }
      }
      this.$api.get("/access_tokens", { params: params})
        .then(
          response => {
            that.access_tokens = response.data.items;
            that.totalAts = response.data.count;
            that.loading = false;
          }
        );
    }
  }
}
</script>
