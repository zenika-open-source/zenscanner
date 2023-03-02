<template>
    <v-card elevation="2" >
    <v-card-title>Last Scans</v-card-title>
    <v-card-text>
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
                        <v-select
                            :items="date_items"
                            v-model="date"
                        ></v-select>
                    </v-col>
                    <v-col></v-col>
                    <v-col></v-col>
                </v-row>
            </v-container>
            
        </template>
        <template v-slot:item="row">
            <ScanRow show_repository :scan="row.item" :repository="row.item.repository"/>
        </template>
        </v-data-table>
    </v-card-text>
  </v-card>
</template>

<script>
import ScanRow from '@/components/scans/ScanRow'
export default {
    name: 'LastScanList',
    components: {
        ScanRow
    },
    data: function () {
        return {
            headers: [
                { text: 'Status', value: '', sortable: false },
                { text: 'Repository', value: 'repository', sortable: false },
                { text: 'Branch', value: 'branch', sortable: false },
                { text: 'Commit', value: 'last_commit', sortable: false },
                { text: 'Plugins', value: '', sortable: false },
                { text: 'Vulnerabilities', value: '', sortable: false,  },
                { text: 'Actions', value: '', sortable: false }
            ],
            scans: [],
            date_items: ['Today', 'Last 7 days'],
            date: "Today",
            totalScans: 0,
            options: {},
            loading: false,
        }
    },
    mounted() {
            this.loadScans();
    },
    watch: {
            options: {
                handler () {this.loadScans()},deep: true,
            },
            date: { 
                handler () { this.options['page'] = 1; this.loadScans(); },
            }
        },
    methods: {
        formatVulnerabilitiesCountText(row, type){
          var count = undefined;
          var new_count = undefined;
          if(type == 'warning'){
            count = row.item.warning_count;
            new_count= row.item.new_warning_count;
          } else if(type == 'none'){
            count = row.item.none_count;
            new_count= row.item.new_none_count;
          } else if(type == 'note'){
            count = row.item.note_count;
            new_count= row.item.new_note_count;
          } else {
            count = row.item.error_count;
            new_count= row.item.new_error_count;
          }
          if(new_count > 0) {
            return new_count+" | Total : "+count;
          }
          else {
            return count
          }
        },
        chipItem(item, t) {
          if(item['matched_scanners']['new'].indexOf(t) > -1){
            return "red";
          } else if(item['matched_scanners']['old'].indexOf(t) > -1) {
            return "orange";
          } else {
            return "green";
          }
        },
        
        loadScans() {
            var that = this;
            this.loading = true;
            let params = {
              'limit': that.options['itemsPerPage'],
              'offset': that.options['itemsPerPage']*(that.options['page']-1),
            }
            params['order_by'] = 'created_at'
            params['ascending'] = 0
            if(this.date == "Last 7 days") {
                params['days'] = 7
            } else {
                params['days'] = 1
            }
            this.$api.get("/scans", {
                params: params,
            }).then(
                response => {
                that.scans = response.data['items'];
                that.totalScans = response.data['count'];
                that.loading = false;
            })
        }
    }
}
</script>