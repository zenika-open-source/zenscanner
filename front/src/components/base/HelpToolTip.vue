<template>
    <v-tooltip bottom>
      <template v-slot:activator="{ on, attrs }">
        <v-icon
          v-bind="attrs"
          v-on="on"
        >
          mdi-help-circle
        </v-icon>
      </template>
      <span>{{ msg }}</span>
    </v-tooltip>
</template>

<script>
export default {
    name: 'HelpToolTip',
    props: ['msg']
}
</script>