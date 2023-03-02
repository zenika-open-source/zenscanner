<template>
  <v-app>
    <v-container fluid fill-height id="login-page">
      <v-layout align-center justify-center>
        <v-flex :style="{ 'max-width': '350px' }">
          <v-card>
            <v-card-text>
              <div class="text-center mb-4">
                <img src="../assets/zensec-rouge.svg" width="120" height="120" />
              </div>

              <transition name="fade" mode="out-in">
                <router-view></router-view>
              </transition>
            </v-card-text>
          </v-card>
        </v-flex>
      </v-layout>
    </v-container>
  </v-app>
</template>

<style scoped>
#login-page {
  background-color: #34495e;
}
</style>