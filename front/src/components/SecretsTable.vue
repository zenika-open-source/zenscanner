<template>
    <div>
        <v-data-table
            :headers="headers"
            :items="secrets"
            :items-per-page="10"
            :options.sync="options"
            :server-items-length="totalSecrets"
            :loading="loading"
            loading-text="Loading... Please wait"
        >
            <template v-slot:top>
            <v-container fluid>
                <v-row>
                    <v-col>
                        <v-text-field append-icon="mdi-magnify" v-model="label" label="Label"></v-text-field>
                    </v-col>
                    <v-col>
                        <v-combobox
                            v-model="select"
                            :items="type_list"
                            label="Credentials Types"
                            multiple
                        ></v-combobox>
                    </v-col>
                    
                    
                </v-row>
            </v-container>
            </template>
            <template v-slot:item="row">
            <tr>
                <td>{{row.item.label}}</td>
                <td>{{ row.item.type }}</td>
                <td>{{row.item.uuid }}</td>
                <td>
                <v-icon @click="openEdit(row.item)">
                    mdi-pencil
                </v-icon>
                <v-icon @click="deleteItem(row.item)">
                    mdi-delete
                </v-icon>
                </td>
            </tr>
            </template>
        </v-data-table>
        <DeleteDialog :enabled="dialogDelete" :confirm="deleteItemConfirm" title="Delete Secret ?" :text="deleteText" :close="closeDelete"/>
        <v-snackbar  v-model="snackbar" timeout="3000">{{ snackbar_text }}</v-snackbar>
        <EditSecretDialog :enabled="dialogEdit" :secret="editedSecret" :cancel="cancelEdit" :success="successEdit"></EditSecretDialog>
    </div>
</template>

<script>

import DeleteDialog from "@/components/base/DeleteDialog.vue"
import EditSecretDialog from "@/components/EditSecretDialog"
export default {
    name: 'SecretsTable',
    components: {
        DeleteDialog,
        EditSecretDialog,
    },
    data: function () {
        return {
            dialogEdit: false,
            dialogDelete: false,
            editedSecret: undefined,
            deleteText: "",
            secrets: undefined,
            options: {},
            label: "",
            snackbar_text: "",
            snackbar: false,
            select: [],
            type_list: undefined,
            totalSecrets: 0,
            loading: false,
            headers: [
                { text: 'Label', value: 'label' },
                { text: 'Type', value: 'type' },
                { text: 'Uuid', value: 'uuid'},
                { text: 'Actions', value: '', sortable: false, }
            ],
        }
    },
    watch: {
        options: {
            handler () {
                this.loadSecrets()
            },
            deep: true,
        },
        select: {
            handler () {
                this.loadSecrets()
            },
            deep: true,
        },
        label: {
            handler () {
                this.options['page'] = 1;
                this.loadSecrets();
            },
        }
    },
    mounted() {
        this.loadSecrets();
        this.loadCredentialTypes();
    },
    methods: {
        openEdit(item){
            this.dialogEdit = true;
            this.editedSecret = item
        },
        cancelEdit() {
            this.dialogEdit = false;
            this.editedSecret = undefined;
        },
        successEdit() {
            this.dialogEdit = false;
            this.editedSecret = undefined;
            this.loadSecrets();
        },
        deleteItem(item){
            this.dialogDelete = true;
            this.deleteText = item.label;
            this.editedSecret = item;
        },
        deleteItemConfirm(){
            this.dialogDelete = false;
            var that = this;
            this.$api.delete("/credentials/" + this.editedSecret.uuid).then(function(){
                that.snackbar_text = "Secret '" + that.editedSecret.label + "' deleted."
                that.snackbar = true
                that.closeDelete()
                that.loadSecrets()
            }).catch(function(){
                that.snackbar_text = "Error during '" + that.editedItem.label + "' deletion."
                that.snackbar = true
                that.closeDelete()
            })
        },
        closeDelete(){
            this.dialogDelete = false;
        },
        loadCredentialTypes(){
            var that = this;
            this.$api.get("/types/credentials").then(
                response => {
                that.type_list = response.data['items']
            })
        },
        loadSecrets() {
            
            this.loading = true;
            var params = new URLSearchParams();
            params.append("limit", this.options['itemsPerPage']);
            params.append("offset", this.options['itemsPerPage']*(this.options['page']-1));
            

            if(this.label != "") {
                params.append("label", this.label);
            }
            if(this.options.sortBy.length > 0){
                params.append("order_by", this.options.sortBy[0]);
                if(this.options.sortDesc[0]){
                params.append("ascending", 1);
                } else {
                params.append("ascending", 0);
                }
            }
            if(this.select.length > 0){
                this.select.forEach(element => {
                    params.append("type", element);
                });
            }
            var that = this;
            this.$api.get("/credentials", {params: params}).then(
                response => {
                that.secrets = response.data['items'];
                that.totalSecrets = response.data['count'];
                that.loading = false;
            })
        }
    }
}
</script>