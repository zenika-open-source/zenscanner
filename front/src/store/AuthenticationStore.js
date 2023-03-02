import Vue from 'vue'
import Vuex from 'vuex'

Vue.use(Vuex)
import router from '../router'

export default new Vuex.Store({
    state: {},
    mutations: {
        LOGIN: (state, next) => {
            window.localStorage.setItem('access_token', next.access_token)
            if(next != undefined) router.push(next.url, () => {});

            
        },
        LOGOUT: () => {
            window.localStorage.removeItem('access_token')
            router.push("/login", () => {});
        },
    },
    getters: {},
    actions: {},
    strict: true,
})
