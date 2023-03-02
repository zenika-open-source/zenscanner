<template>
    <div>
        <v-dialog v-model="enabled" max-width="500px">
            <v-card>
                <v-card-title class="text-h5">New Scan for {{ repository.name }}</v-card-title>
                <v-card-text class="card-title-item">
                    <v-form
                        ref="form"
                        v-model="valid"
                        lazy-validation
                    >
                        <v-select
                            v-model="select"
                            :items="branches"
                            :rules="[v => !!v || 'Branch is required']"
                            label="Branch"
                            required
                        ></v-select>
                    </v-form>
                </v-card-text>
                <v-card-actions>
                    <v-spacer></v-spacer>
                    <v-btn depressed @click="close">Cancel</v-btn>
                    <v-btn depressed color="success" @click="confirm" :disabled="!isFormValid">Run Scan</v-btn>
                    <v-btn class="mr-4" color="primary" @click="refreshBranch" :loading="refreshBranchLoader"><v-icon>mdi-refresh</v-icon></v-btn>
                    <v-spacer></v-spacer>
                </v-card-actions>
            </v-card>
            
        </v-dialog>
        <v-snackbar v-model="snackbar" timeout="3000">{{ snackbar_text }}</v-snackbar>
    </div>
    
</template>

<script>
export default {
    name: 'NewScanDialog',
    props: ['enabled', 'success', 'cancel', 'repository'],
    computed: {
        isFormValid: function () {
            return (this.select != "")
        },
    },
    methods: {
        close () {
            this.cancel();
        },
        confirm() {
            if(this.isFormValid) {
                var data = {
                    'branch': this.select,
                }
                var that = this;
                this.$api.post("/repositories/" + this.repository.uuid + "/scan", data).then(() => {
                    that.snackbar_text = "Scan created for branch " + that.select
                    that.snackbar = true;
                    that.success();
                })
            }
        },
        refreshBranch(){
            var that = this;
            this.refreshBranchLoader = true;
            this.$api.get("/repositories/" + this.repository.uuid + "?refresh_branches").then(
                response => {
                that.refreshBranchLoader = false;
                that.branches = response.data['branches']
            })
        },
    },
    mounted() {
        this.branches = this.repository.branches
    },
    data: function () {
        return {
            valid: false,
            branches: undefined,
            select: "",
            snackbar: false,
            snackbar_text: "",
            refreshBranchLoader: false
        }
    },
}
</script>