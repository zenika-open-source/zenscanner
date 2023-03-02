<template>
    <v-dialog v-model="enabled" max-width="500px">
        <v-card>
        <v-card-title class="text-h5">{{ title }}</v-card-title>
        <v-card-text v-if="text" class="card-title-item"><p>{{ text }}</p></v-card-text>
        <v-card-actions>
            <v-spacer></v-spacer>
            <v-btn depressed @click="close">Cancel</v-btn>
            <v-btn depressed color="error" @click="confirm">OK</v-btn>
            <v-spacer></v-spacer>
        </v-card-actions>
        </v-card>
    </v-dialog>
</template>

<style scoped>
.card-title-item p {
  width: 100%;
  text-align: center;
  color: red;
}
</style>

<script>
export default {
    name: 'DeleteDialog',
    props: ['confirm', 'title', 'text', 'enabled', 'close']
}
</script>