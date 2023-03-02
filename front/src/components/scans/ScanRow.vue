<template>
    <tr>
            <td>
                <v-chip v-if="scan.status == 'SUCCESS'" class="ma-2" color="green" label text-color="white"><v-icon>mdi-check-circle</v-icon></v-chip>
                <v-chip v-if="scan.status == 'PENDING'" class="ma-2" color="orange" label text-color="white"><v-icon>mdi-pause-circle</v-icon></v-chip>
                <v-chip v-if="scan.status == 'RECEIVED'" class="ma-2" color="orange" label text-color="white"><v-icon>mdi-pause-circle</v-icon></v-chip>
                <v-chip v-if="scan.status == 'RETRY'" class="ma-2" color="orange" label text-color="white"><v-icon>mdi-pause-circle</v-icon></v-chip>
                <v-chip v-if="scan.status == 'RUNNING'" class="ma-2" color="blue" label text-color="white"><v-icon>mdi-play-circle</v-icon></v-chip>
                <v-chip v-if="scan.status == 'FAILURE'" class="ma-2" color="red" label text-color="white"><v-icon>mdi-alert-circle</v-icon></v-chip>
                <v-chip v-if="scan.status == 'REVOKED'" class="ma-2" color="red" label text-color="white"><v-icon>mdi-alert-circle</v-icon></v-chip>
            </td>
            <td v-if="show_repository != undefined"><a target="_blank" :href="scan.repository.url">{{ scan.repository.name }}</a></td>
            <td>
                <span v-if="scan.branch_url == ''">{{ short_branch()}}</span><a v-else target="_blank" :href="scan.branch_url">{{ short_branch()}}</a>
            </td>
            <td v-if="show_date != undefined">{{ scan.created_at | moment }}</td>
            <td>
              <span v-if="scan.commit_url == ''">{{scan.last_commit.slice(0,7)}}</span><a v-else target="_blank" :href="scan.commit_url">{{scan.last_commit.slice(0,7)}}</a>
            </td>
            <td>
              <v-chip class="ma-2" v-for="t in scan['scanners']" v-bind:key="t" :color="chipItem(t)">{{ t }}</v-chip>
            </td>
            <td>
              <v-chip color="red" label text-color="white">
                <v-icon v-if="scan.new_error_count > 0" left>mdi-alert-decagram</v-icon> {{ formatVulnerabilitiesCountText('error') }}
              </v-chip>

              <v-chip class="ma-2" color="orange" label text-color="white" >
                <v-icon v-if="scan.new_warning_count > 0" left>mdi-alert-decagram</v-icon> {{ formatVulnerabilitiesCountText('warning') }}
              </v-chip>

              <v-chip class="ma-2" color="yellow" label text-color="white">
                <v-icon v-if="scan.note_count > 0" left>mdi-alert-decagram</v-icon> {{ formatVulnerabilitiesCountText('note') }}
              </v-chip>
              
              <v-chip class="ma-2" color="blue" label text-color="white">
                <v-icon v-if="scan.new_none_count > 0" left>mdi-alert-decagram</v-icon> {{ formatVulnerabilitiesCountText('none') }}
              </v-chip>
            </td>
            <td>
                <ToolTipAction v-if="show_repository != undefined" msg="View Repository" icon="folder" :url="{ name: 'repository', params: { repoUuid: scan.repository.uuid }}"/>
                <ToolTipAction msg="View Scan Vulnerabilities" icon="eye" :url="{ name: 'scan', params: { scanUuid: scan.uuid }}"/>
                <ToolTipAction msg="Download SARIF report" icon="download" :callback="downloadResult"/>
                <ToolTipAction :msg="'Run Scan on branch '+scan.branch " icon="magnify-scan" :callback="runScan"/>
            </td>
          </tr>
</template>

<script>
import ToolTipAction from "@/components/base/ToolTipAction.vue";
import moment from 'moment'
export default {
    name: 'ScanRow',
    props: ['scan', 'runcallback', 'show_date', 'show_repository', 'repository'],
    components: {
      ToolTipAction
    },
    filters: {
      moment: function (date) {
        return moment(date).calendar();
      }
    },
    methods: {
        runScan() {
          this.$api.post("/repositories/" + this.repository.uuid + "/scan", {"branch": this.scan.branch}).then(() => {
              this.runcallback();
          })
        },
        chipItem(t) {
          if(this.scan['matched_scanners']['new'].indexOf(t) > -1){
            return "red";
          } else if(this.scan['matched_scanners']['old'].indexOf(t) > -1) {
            return "orange";
          } else {
            return "green";
          }
        },
        downloadResult() {
            var that = this;
            this.$api.get('/scans/'+this.scan.uuid+'/sarif')
            .then((response) => {
                    var fileURL = window.URL.createObjectURL(new Blob([JSON.stringify(response.data)]));
                    var fileLink = document.createElement('a');

                    fileLink.href = fileURL;
                    fileLink.setAttribute('download', that.repository.name+' ('+that.scan.branch+') '+that.scan.uuid+'.sarif');
                    document.body.appendChild(fileLink);

                    fileLink.click();
            });
        },
        formatVulnerabilitiesCountText(type){
          var scan = this.scan;
          var count = undefined;
          var new_count = undefined;
          if(type == 'warning'){
            count = scan.warning_count;
            new_count= scan.new_warning_count;
          } else if(type == 'none'){
            count = scan.none_count;
            new_count= scan.new_none_count;
          } else if(type == 'note'){
            count = scan.note_count;
            new_count= scan.new_note_count;
          } else {
            count = scan.error_count;
            new_count= scan.new_error_count;
          }
          if(new_count > 0) {
            return new_count+" | Total : "+count;
          }
          else {
            return count
          }
        },
        short_branch () {
          var branch = this.scan.branch
          if(branch.length < 30){
            return branch
          } else {
            return branch.slice(0, 27) + "..."
          }
        }
    }
}
</script>