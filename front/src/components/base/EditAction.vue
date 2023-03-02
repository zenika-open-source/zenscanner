<template>
    <v-icon @click="goto()">
        mdi-pencil
    </v-icon>
</template>
<script>
export default {
  name: 'EditAction',
  props: ['url'],
  methods: {
      goto () {
          this.$router.push(this.url)
      }
  }
}
</script>