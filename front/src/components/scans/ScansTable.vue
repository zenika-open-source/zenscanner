<template>
    <v-data-table
          :headers="headers"
          :items="scans"
          :items-per-page="10"
          :options.sync="options"
          :server-items-length="totalScans"
          :loading="loading"
          loading-text="Loading... Please wait"
      >
        <template v-slot:top>
            <v-container fluid>
            <v-row>
              <v-col>
                <v-text-field
                    v-model="search.branch"
                    label="Branch"
                    class="mx-4"
                    append-icon="mdi-magnify"
                ></v-text-field>
              </v-col>
              <v-col>
                <v-text-field
                    v-model="search.last_commit"
                    label="Last Commit"
                    class="mx-4"
                    append-icon="mdi-magnify"
                ></v-text-field>
              </v-col>
              <v-col>
                <v-select
                  v-model="search.level"
                  :items="levels"
                  label="Vulnerability level"
                  multiple
                ></v-select>
              </v-col>
            </v-row>
            </v-container>
      </template>
      <template v-slot:item="row">
          <ScanRow show_date :scan="row.item" :runcallback="loadScans" :repository="repository"/>
      </template>
    </v-data-table>
</template>

<script>
import ScanRow from '@/components/scans/ScanRow'
export default {
    name: 'ScansTable',
    components: {
      ScanRow
    },
    props: ['repository'],
    data: function () {
      return {
        headers: [
          { text: 'Status', value: '', sortable: false },
          { text: 'Branch', value: 'branch' },
          { text: 'Date', value: 'created_at' },
          { text: 'Last Commit', value: 'last_commit' },
          { text: 'Plugins', value: '', sortable: false },
          { text: 'Vulnerabilities', value: '', sortable: false,  },
          { text: 'Actions', value: '', sortable: false }
        ],
        scans: undefined,
        loading: false,
        search: {
          "level": [],
          "last_commit" : "",
          "branch" : "",
        },
        levels: [
          {'text': 'High', 'value': 3},
          {'text': 'Medium', 'value': 2},
          {'text': 'Low', 'value': 1},
          {'text': 'Info', 'value': 0},
        ],
        totalScans:0,
        options: {},
        uuid: this.$route.params.repoUuid,
        timer: undefined
      }
    },
    watch: {
        options: {
        handler () {
            this.loadScans()
        },
        deep: true,
        },
        search: {
        handler () {
            this.options['page'] = 1;
            this.loadScans();
        },
        deep: true,
        }
    },
    mounted() {
        this.loadScans();
    },
    destroyed() {
        this.clearTimer();
    },
    methods: {
        clearTimer() {
            if(this.timer != undefined) {
                clearInterval(this.timer);
                this.timer = undefined;
            }
        },
        setTimer(){
            if(this.timer == undefined) {
                this.timer = setInterval(this.loadScans, 10000);
            }
        },
        loadScans() {
            var that = this;
            this.loading = true;
            var params = new URLSearchParams();
            params.append("limit", this.options['itemsPerPage']);
            params.append("offset", this.options['itemsPerPage']*(this.options['page']-1));
            
            if(this.options.sortBy.length > 0){
                params.append("order_by", this.options.sortBy[0]);
                if(this.options.sortDesc[0]){
                params.append("ascending", 1);
                } else {
                params.append("ascending", 0);
                }
            }

            ['branch', 'last_commit'].forEach(element => {
                if(that.search[element] != ""){
                    params.append(element, that.search[element]);
                }
            });

            this.search.level.forEach(element => {
                params.append("level", element);
            });
            this.$api.get("/repositories/"+this.$route.params.repoUuid+"/scans", {params: params})
            .then(
                response => {
                that.scans = response.data['items'];
                that.totalScans = response.data['count'];
                that.loading = false;
                that.clearTimer();
                that.scans.forEach(element => {
                    if (['PENDING', 'RECEIVED', 'RETRY', 'RUNNING'].indexOf(element.status) > -1) {
                        that.setTimer();
                    }
                });
            })
        }
    }
}
</script>