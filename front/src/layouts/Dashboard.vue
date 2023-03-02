<template>
  <div>
  <v-app-bar
      color="deep-purple"
      dark
    >
      <v-toolbar-title>ZenScanner</v-toolbar-title>
      <v-spacer></v-spacer>
      <v-btn icon @click.prevent="Logout">
        <v-icon>mdi-logout</v-icon>
      </v-btn>
      <template v-slot:extension>
        <v-tabs centered>
          <v-tab v-bind:key="tab.title" v-for="tab in tabs" :to="tab.link"><v-icon left>{{ tab.icon }}</v-icon> {{ tab.title }}</v-tab>
        </v-tabs>
      </template>
    </v-app-bar>
    <v-app>
        <router-view></router-view>
    </v-app>
    </div>
</template>

<script>
import store from '../store/AuthenticationStore'
export default {
  name: "App",
  methods: {
    Logout(){
      this.$api.get("/auth/logout").then(function(){
        store.commit('LOGOUT');
      })
      
    }
  },
  data() {
    return {
      drawer: false,
      group: null,
      router: this.$router,
      tabs: [{
        title: 'Home',
        link: '/',
        icon: 'mdi-home'
      },{
        title: 'Repositories',
        link: '/repositories',
        icon: 'mdi-folder'
      },{
        title: 'Vulnerabilities',
        link: '/vulnerabilities',
        icon: 'mdi-bug'
      },{
        title: 'Access Tokens',
        link: '/access_tokens',
        icon: 'mdi-account-key'
      },{
        title: 'Secrets',
        link: '/secrets',
        icon: 'mdi-lock'
      }
    ]
    };
  },
};
</script>
