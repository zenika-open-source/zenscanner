<template>
  <v-icon @click="action()" >
      mdi-{{ icon }}
  </v-icon>
</template>
<script>
export default {
  name: 'IconAction',
  props: ['url', 'icon', 'callback'],
  methods: {
      action () {
          this.$router.push(this.url)
      }
  }
}
</script>