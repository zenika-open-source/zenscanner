<template>
  <v-form ref="form" @submit.prevent="Register">
    <v-text-field
      label="Username"
      prepend-icon="mdi-account"
      v-model="login"
      required
      :rules="[v => !!v || 'Item is required']"
      :error-messages="error"
    ></v-text-field>
    <v-text-field
      label="Email"
      prepend-icon="mdi-account"
      v-model="email"
      type="email"
      :rules="[v => !!v || 'Item is required']"
      required
      :error-messages="error"
    ></v-text-field>

    <v-text-field
      label="Password"
      prepend-icon="mdi-lock"
      type="password"
      :rules="[v => !!v || 'Item is required']"
      v-model="password"
      required
    ></v-text-field>
    <v-text-field
      label="Password Confirmation"
      :rules="[v => !!v || 'Item is required']"
      prepend-icon="mdi-lock"
      type="password"
      v-model="passwordconfirm"
      required
    ></v-text-field>

    <v-btn class="mr-4" :loading="loading" color="success" type="submit">Create an account</v-btn>
    <v-btn class="mr-4" color="primary" @click="$router.push('/login')">Login</v-btn>
    <v-snackbar  v-model="snackbar" timeout="3000">{{ snackbar_text }}</v-snackbar>
  </v-form>
</template>

<script>
export default {
  name: 'Register',
  props: {
    msg: String
  },
  data: function () {
    return {
      error: undefined,
      success: undefined,
      password: undefined,
      login: undefined,
      loading: false,
      passwordconfirm: undefined,
      email: undefined,
      snackbar: false,
      snackbar_text: ""

    }
  },
  methods: {
    Register(){
      if(this.login && this.password && this.email && this.password == this.passwordconfirm){
        this.loading = true;
        var that = this;
        var params = {
          "username"            : this.login,
          "password"            : this.password,
          "email"               : this.email,
          "passwordConfirmation": this.passwordconfirm,
      }
        this.$api.post("/auth/register", params).then(
        response => {
            that.error = undefined;
            that.loading = false;
            that.snackbar_text = response.data.message;
            that.snackbar = true
            
        })
        .catch(function(error) {
          that.error = error.response.data.message;
          that.loading = false;
        })
      }   
    }
  }
}
</script>

<!-- Add "scoped" attribute to limit CSS to this component only -->
<style scoped>
h3 {
  margin: 40px 0 0;
}
ul {
  list-style-type: none;
  padding: 0;
}
li {
  display: inline-block;
  margin: 0 10px;
}
a {
  color: #42b983;
}
</style>
