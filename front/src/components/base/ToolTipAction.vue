<template>
    <v-tooltip bottom>
      <template v-slot:activator="{ on, attrs }">
        <v-icon v-bind="attrs" v-on="on" @click="action()">
            mdi-{{ icon }}
        </v-icon>
      </template>
      <span>{{ msg }}</span>
    </v-tooltip>
</template>
<script>
export default {
  name: 'ToolTipAction',
  props: ['url', 'icon', 'msg', 'callback', 'args'],
  methods: {
      action () {
          if (this.url != undefined){
            this.$router.push(this.url)
          } else if (this.callback != undefined){
              if (this.args != undefined) {
                this.callback(this.args);
              } else {
                this.callback();
              }
          }
          
      }
  }
}
</script>
