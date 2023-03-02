<template>
  <v-form ref="form" @submit.prevent="Login">
    <v-text-field
      label="Username"
      prepend-icon="mdi-account"
      v-model="login"
      required
      :error-messages="error"
    ></v-text-field>

    <v-text-field
      label="Password"
      prepend-icon="mdi-lock"
      type="password"
      v-model="password"
      required
    ></v-text-field>
    <div style="text-align:center">
      <v-btn class="mr-4 login-btn" :loading="loading" color="success" type="submit">Login</v-btn>
    <v-btn class="mr-4 login-btn" color="primary" @click="$router.push('/register')">Register</v-btn>
    </div>
  </v-form>
</template>

<script>
import store from '../store/AuthenticationStore'

export default {
  name: 'Login',
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
    }
  },
  methods: {
    Login(){
      
      if(this.login && this.password){
        this.loading = true;
        var that = this;
        this.$api.post("/auth/login",
        {
            username: that.login,
            password: that.password,
        }).then(
        response => {
            that.error = undefined;
            that.loading = false;
            if(response.status == 200) { 
              store.commit('LOGIN', {"url": '/', "access_token": response.data.access_token}); 
            }
            
        })
        .catch(function(error) {
          if (error.response && error.response.status === 401) {
            that.error = error.response.data.message;
            that.loading = false;
          }
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
.login-btn {
  margin-left: 20px;
  margin-right: 20px;
}
.login-btn:first-child {
  margin-left: 0px
}
.login-btn:nth-child(n+1) {
  margin-right: 0px;
}
</style>
