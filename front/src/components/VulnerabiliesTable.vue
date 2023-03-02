<template>
    <v-data-table
          :headers="headers"
          :items="vulns"
          :items-per-page="10"
          :options.sync="options"
          :server-items-length="totalVulns"
          :loading="loading"
          loading-text="Loading... Please wait"
      >
        <template v-slot:top>
          <VulnerabilityViewer :enabled="viewerEnabled" :uuid="selectedVulnerability" :close="closeViwer"/>
          <v-container fluid>
            <v-row>
              <v-col>
                <v-select
                  v-model="search.level"
                  :items="levels"
                  label="Level"
                  item-text="text"
                  item-value="value"
                  multiple
                ></v-select>
              </v-col>
              <v-col>
                <v-select
                  v-model="search.tool"
                  :items="tools"
                  label="Tool"
                  multiple
                ></v-select>
              </v-col>
              <v-col>
                <v-select
                  v-model="search.new"
                  :items="new_states"
                  label="Is New ?"
                  item-text="text"
                  item-value="value"
                ></v-select>
              </v-col>
              <v-col><v-text-field v-model="search.author_email" label="Commit Author" append-icon="mdi-magnify" ></v-text-field></v-col>
              
            </v-row>
            <v-row>
              <v-col><v-text-field v-model="search.rule" label="Rule" append-icon="mdi-magnify" ></v-text-field></v-col>
              <v-col><v-text-field v-model="search.path" label="File" append-icon="mdi-magnify" ></v-text-field></v-col>
              <v-col><v-text-field v-model="search.details" label="Details" append-icon="mdi-magnify" ></v-text-field></v-col>
            </v-row>
          </v-container>
          
      </template>
      <template v-slot:item="row">
          <tr>
            <td>{{ row.item.tool }}</td>
            <td>{{ row.item.rule }}</td>
            <td>
              <a :href="row.item.vulnerability_url" target="_blank" v-if="row.item.vulnerability_url != ''">{{ row.item.path }}</a>
              <span v-else>{{ row.item.path }}</span>
            </td>
            <td>{{ row.item.details }}</td>
            <td>{{ row.item.author_email }}</td>
            <td>
              <VulnerabilityChip :vulnerability="row.item"/>
            </td>
            <td>
              <v-menu
            bottom
            left
          >
            <template v-slot:activator="{ on, attrs }">
              <v-btn
                icon
                v-bind="attrs"
                v-on="on"
              >
                <v-icon>mdi-dots-vertical</v-icon>
              </v-btn>
            </template>

            <v-list>
                <v-list-item @click="openViewer(row.item)" >
                  <v-icon >mdi-eye</v-icon> View
                </v-list-item>
                <v-list-item @click="openCommitCode(row.item.commit_url)" >
                  <v-icon >mdi-code-tags</v-icon> View Code
                </v-list-item>
            </v-list>
          </v-menu>
            </td>
          </tr>
      </template>
    </v-data-table>
</template>

<script>
import VulnerabilityViewer from '@/components/VulnerabilityViewer'
import VulnerabilityChip from '@/components/base/VulnerabilityChip'
export default {
    name: 'VulnerabiliesTable',
    components: {
      VulnerabilityViewer,
      VulnerabilityChip
    },
    props: ['scanUUID', 'scan'],
    data: function () {
      return {
        headers: [
          { text: 'Tool', value: 'tool' },
          { text: 'Rule', value: 'rule' },
          { text: 'File', value: 'path' },
          { text: 'Details', value: 'details',},
          { text: 'Commit Author', value: 'author_email',},
          { text: 'Level', value: 'level', sortable: false  },
          { text: 'Actions', value: '', sortable: false  },
        ],
        levels: [
          {'text': 'Error', 'value': 3},
          {'text': 'Warning', 'value': 2},
          {'text': 'Note', 'value': 1},
          {'text': 'None', 'value': 0},
        ],
        tools: [],
        vulns: undefined,
        loading: false,
        viewerEnabled: false,
        selectedVulnerability: undefined,
        new_states: [
          {'text': '', 'value': ''},
          {'text': 'Yes', 'value': '1'},
          {'text': 'No', 'value': '0'},
        ],
        search: {
          "level": [],
          "tool": [],
          "rule": "",
          "path": "",
          "details": "",
          "new": "",
          "author_email" : ""
        },
        totalVulns:0,
        options: {},
      }
    },
    watch: {
      options: {
        handler () {
            this.loadVulnerabilities()
        },
        deep: true,
        },
        search: {
          handler () {
            this.options['page'] = 1;
            this.loadVulnerabilities();
          },
          deep: true,
        }
    },
    mounted() {
        this.loadTools();
    },
    methods: {
      openViewer(item) {
        this.selectedVulnerability = item.uuid;
        this.viewerEnabled = true;
      },
      closeViwer() {
        this.viewerEnabled = false;
      },
      openCommitCode (url) {
        window.open(url, '_blank')
      },
      loadTools() {
        if(this.scan != undefined) {
          this.tools = [];
          this.scan.matched_scanners['old'].forEach(element => {
            if(this.tools.indexOf(element) == -1) {
              this.tools.push(element);
            }
          });
          this.scan.matched_scanners['new'].forEach(element => {
            if(this.tools.indexOf(element) == -1) {
              this.tools.push(element);
            }
          });
        } else {
          var that = this;
          this.$api.get("/types/scanners").then(
            response => {
              that.tools = response.data['items']
          })
        }
      },
      loadVulnerabilities() {
        var that = this;
        this.loading = true;
        var params = new URLSearchParams();
        params.append("offset", this.options['itemsPerPage']*(this.options['page']-1));
        params.append("limit", this.options['itemsPerPage']);
        
        if(this.options.sortBy.length > 0){
            params.append("order_by", this.options.sortBy[0]);
            if(this.options.sortDesc[0]){
            params.append("ascending", 1);
            } else {
            params.append("ascending", 0);
            }
        }

        this.search.level.forEach(element => {
          params.append("level", element);
        });

        this.search.tool.forEach(element => {
          params.append("tool", element);
        });
        ['rule', 'path', 'details', 'new', 'author_email'].forEach(element => {
          if(that.search[element] != ""){
            params.append(element, that.search[element]);
          }
        });

        if (this.scanUUID) {
          params.append('scan', this.scanUUID)
        }
        this.$api.get("/vulnerabilities", {
            params: params,
        }).then(
            response => {
            that.vulns = response.data['items'];
            that.totalVulns = response.data['count'];
            that.loading = false;
        })
      }
    }
}
</script>