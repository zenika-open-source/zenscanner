<template>
  <div>
  <v-data-table
          :headers="headers"
          :items="repositories"
          :items-per-page="10"
          :options.sync="options"
          :server-items-length="totalRepositories"
          :loading="loading"
          loading-text="Loading... Please wait"
      >
        <template v-slot:top>
          <v-container fluid>
          <v-row>
            <v-col>
              <v-text-field
                v-model="search"
                label="Search"
                append-icon="mdi-magnify"
              ></v-text-field>
            </v-col>
            
          </v-row>
          </v-container>
        </template>
      <template v-slot:item="row">
          <tr>
            <td>{{row.item.name}}</td>
            <td>
              <v-icon>{{ icon(row.item.source_control) }}</v-icon>
               <a :href="row.item.url">{{ row.item.url }}</a></td>
            <td>{{row.item.scan_count }}</td>
            <td>
              <ToolTipAction msg="View Repository" icon="eye" :url="{ name: 'repository', params: { repoUuid: row.item.uuid }}"/>
              <EditAction :url="{ name: 'edit_repository', params: { repoUuid: row.item.uuid }}"/>
              <v-icon @click="deleteItem(row.item)">
                mdi-delete
              </v-icon>
            </td>
          </tr>
      </template>
      </v-data-table>
      <DeleteDialog :enabled="dialogDelete" :confirm="deleteItemConfirm" title="Delete Repository ?" :text="deleteText" :close="closeDelete"/>
    <v-snackbar  v-model="snackbar" timeout="3000">{{ snackbar_text }}</v-snackbar>
  </div>
</template>

<script>
import ToolTipAction from "@/components/base/ToolTipAction.vue";
import EditAction from "@/components/base/EditAction.vue";
import DeleteDialog from "@/components/base/DeleteDialog.vue"
export default {
  name: 'RepositoriesTable',
  components: {
    ToolTipAction,
    EditAction,
    DeleteDialog
  },
  data: function () {
      return {
        loading: false,
        repositories: [],
        totalRepositories: 0,
        dialogDelete: false,
        editedItem: undefined,
        snackbar: false,
        snackbar_text: undefined,
        deleteText: undefined, 
        options: {},
        search: "",
        headers: [
          { text: 'Name', value: 'name' },
          { text: 'URL', value: 'url' },
          { text: 'Scans count', value: 'scan_count'},
          { text: 'Actions', value: '', sortable: false, }
        ],
      }
    },
  watch: {
    options: {
      handler () {
        this.loadRepositories()
      },
      deep: true,
    },
    search: {
      handler () {
        this.options['page'] = 1;
        this.loadRepositories();
      },
      deep: true,
    }
  },
  mounted() {
    this.loadRepositories();
  },
  methods: {
    deleteItem (item) {
      this.deleteText = item.name;
      this.editedItem = item;
      this.dialogDelete = true
    },
    deleteItemConfirm () {
      var that = this;
      this.$api.delete("/repositories/" + that.editedItem.uuid).then(function(){
          that.snackbar_text = "Repository '" + that.editedItem.name + "' deleted."
          that.snackbar = true
          that.closeDelete()
          that.loadRepositories()
      }).catch(function(){
          that.snackbar_text = "Error during '" + that.editedItem.name + "' deletion."
          that.snackbar = true
          that.closeDelete()
      })
      
    },
    icon(sc){
      if(sc == "git") return "mdi-git";
      if(sc == "svn") return "mdi-tortoise";
      return ""
    },
    closeDelete () {
      this.editedItem = undefined
      this.dialogDelete = false
    },
    loadRepositories() {
      var that = this;
      this.loading = true;
      let params = {
        'limit': that.options['itemsPerPage'],
        'offset': that.options['itemsPerPage']*(that.options['page']-1),
      }
      if(this.search != "") {
        params['search'] = this.search;
      }
      if(this.options.sortBy.length > 0){
        params['order_by'] = this.options.sortBy[0]
        if(this.options.sortDesc[0]){
          params['ascending'] = 1
        } else {
          params['ascending'] = 0
        }
      }
      this.$api.get("/repositories", {
        params: params,
       }).then(
        response => {
          that.repositories = response.data['items'];
          that.totalRepositories = response.data['count'];
          that.loading = false;
      })
    }
  }
}
</script>