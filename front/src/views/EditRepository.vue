<template>
    <v-container>
    <v-card>
      <v-card-title>
        Edit Repository
      </v-card-title>
      <v-card-text>
        <v-form
            ref="form"
            v-model="valid"
            lazy-validation
        >
            <v-text-field
            v-model="name"
            :rules="[v => !!v || 'Name is required']"
            label="Name"
            required
            ></v-text-field>

            <v-text-field
            v-model="url"
            label="Url"
            :rules="[v => !!v || 'Url is required']"
            required
            ></v-text-field>
            <v-row>
                <v-col>
                    <v-select
                    v-model="secret"
                    :items="secrets"
                    item-text="label"
                    item-value="uuid"
                    label="Secret"
                    required
                    ></v-select>
                </v-col>
                <v-col>
                    <v-btn class="mr-4" color="success" @click="dialogNew=true">New Secret</v-btn>
                </v-col>
            </v-row>
            
            

            <v-btn
            :disabled="!isFormValid"
            color="success"
            class="mr-4"
            @click="validate"
            >
            Update
            </v-btn>
        </v-form>
      </v-card-text>
    </v-card>
    <NewSecretDialog :enabled="dialogNew" :cancel="closeNewSecret" :success="successNewSecret"/>
    <v-snackbar v-model="snackbar" timeout="3000">{{ snackbar_text }}</v-snackbar>
  </v-container>
</template>

<script>
import NewSecretDialog from '@/components/NewSecretDialog'
export default {
    name: 'EditRepository',
    components: {
        NewSecretDialog
    },
    data: function () {
      return {
        secrets: undefined,
        raw_secrets: undefined,
        name: "",
        url: "",
        secret: '',
        valid: undefined,
        snackbar: false,
        snackbar_text: "",
        dialogNew: false,
      }
    },
    computed: {
        isFormValid: function () {
            return (this.url != "" && this.name != "")
        },
    },
    mounted() {
        this.loadRepositoryInformations();
        this.loadSecrets();
    },
    methods: {
        loadRepositoryInformations() {
            var that = this;
            
            this.$api.get("/repositories/"+this.$route.params.repoUuid).then(
                response => {
                that.name = response.data.name;
                that.url = response.data.url;
                that.secret = response.data.credential;
            })
        },
        loadSecrets() {
            var that = this;
            this.loading = true;
            this.$api.get("/credentials").then(
                response => {
                    that.secrets = [{'label':'No Secret', 'uuid': ''}]
                    response.data['items'].forEach(element => {
                        that.secrets.push(element);
                    });
                    that.loading = false;
            })
        },
        validate() {
            if(this.isFormValid) {
                var data = {
                    'name': this.name,
                    'url': this.url,
                }
                if(this.secret != ''){
                    data['credential'] = this.secret
                }
                var that = this;
                this.$api.put("/repositories/" + this.$route.params.repoUuid, data).then(() => {
                    this.$router.push('/repositories')
                }).catch(() => {
                    that.snackbar_text = "Error during repository creation."
                    that.snackbar = true;
                })
            }
        },
        newSecret() {

        },
        closeNewSecret () {
            this.dialogNew = false;
        },
        successNewSecret() {
            this.dialogNew = false;
            this.loadSecrets()
        }
    }
}
</script>