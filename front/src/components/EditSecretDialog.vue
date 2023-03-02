<template>
    <div>
        <v-dialog v-model="enabled" max-width="500px">
            <v-card>
                <v-card-title class="text-h5">Edit secret</v-card-title>
                <v-card-text class="card-title-item">
                    <v-form
                        ref="form"
                        v-model="valid"
                        lazy-validation
                    >
                        <v-text-field
                            v-model="label"
                            label="Label"
                            :rules="[v => !!v || 'Item is required']"
                            required
                        ></v-text-field>

                        <v-text-field
                            v-model="value"
                            label="Value"
                            :rules="[v => !!v || 'Item is required']"
                            required
                        ></v-text-field>

                        <v-select
                            v-model="select"
                            :items="types"
                            :rules="[v => !!v || 'Item is required']"
                            label="Secret Type"
                            required
                        ></v-select>

                    </v-form>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn depressed @click="close">Cancel</v-btn>
                    <v-btn depressed color="success" @click="confirm" :disabled="!isFormValid">Edit</v-btn>
                    <v-spacer></v-spacer>
                </v-card-actions>
            </v-card>
            
        </v-dialog>
        <v-snackbar v-model="snackbar" timeout="3000">{{ snackbar_text }}</v-snackbar>
    </div>
    
</template>

<script>
export default {
    name: 'EditSecretDialog',
    props: ['enabled', 'success', 'cancel', 'secret'],
    computed: {
        isFormValid: function () {
            return (this.label != "" && this.value != "" && this.select != "")
        },
    },
    watch: {
        secret: {
            handler () {
                this.feedSecret()
            },
            deep: true,
        },
    },
    methods: {
        feedSecret() {
            if (this.secret != undefined){
                this.label = this.secret.label;
                this.select = this.secret.type;
                this.uuid = this.secret.uuid;
                this.value = undefined;
            } else {
                this.label = undefined;
                this.select = undefined;
                this.uuid = undefined;
                this.value = undefined;
            }
            
        },
        close () {
            this.cancel();
        },
        confirm() {
            if(this.isFormValid) {
                var data = {
                    'label': this.label,
                    'type': this.select,
                    'value': this.value,
                }
                var that = this;
                this.$api.put("/credentials/" + this.uuid,data).then(() => {
                    that.snackbar_text = "Secret updated"
                    that.snackbar = true;
                    this.success();
                }).catch(() => {
                    that.snackbar_text = "Failed to update secret"
                    that.snackbar = true;
                })
            }
        },
        loadCredentialTypes(){
            var that = this;
            this.$api.get("/types/credentials").then(
                response => {
                that.types = response.data['items']
            })
        },
    },
    mounted() {
        this.loadCredentialTypes();
    },
    data: function () {
        return {
            valid: false,
            uuid: undefined,
            value: "",
            label: "",
            types: undefined,
            select: "",
            snackbar: false,
            snackbar_text: "",
        }
    },
}
</script>